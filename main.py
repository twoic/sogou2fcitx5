#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from pathlib import Path
from sougou_downloader import SougouSpider

# ==== 所有可用分类 ====
ALL_CATEGORIES = {
    "城市信息": 167,
    "自然科学": 1,
    "社会科学": 76,
    "工程应用": 96,
    "农林渔畜": 127,
    "医学医药": 132,
    "电子游戏": 436,
    "艺术设计": 154,
    "生活百科": 389,
    "运动休闲": 367,
    "人文科学": 31,
    "娱乐休闲": 403,
}

# ==== 解析命令行参数 ====
parser = argparse.ArgumentParser(description="搜狗拼音词库下载工具")
parser.add_argument("--recommended", action="store_true", help="仅下载官方推荐词库")
parser.add_argument("--workers", type=int, default=None, help="最大线程数（默认智能分配）")
parser.add_argument(
    "--categories",
    type=int,
    nargs="*",
    help="指定要下载的分类 ID（多个用空格分隔，如：1 132 436）",
)
args = parser.parse_args()

# ==== 基础路径 ====
base_path = Path(__file__).resolve().parent
save_path = base_path / "sogou_scel"

# ==== 筛选分类 ====
if args.categories:
    categories = {k: v for k, v in ALL_CATEGORIES.items() if v in args.categories}
    if not categories:
        print("❌ 无效的分类 ID，请检查输入。")
        exit(1)
else:
    categories = ALL_CATEGORIES

# ==== 初始化爬虫 ====
spider = SougouSpider(max_workers=args.workers)

# ==== 主执行逻辑 ====
for cate_name, cate_id in categories.items():
    cate_url = f"https://pinyin.sogou.com/dict/cate/index/{cate_id}"
    cate_dir = save_path / str(cate_id)
    cate_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🗂️ 正在处理大类：{cate_name}（ID: {cate_id}）")

    # 获取子类列表
    resp = spider.get_html(cate_url)
    sub_cates = (
        spider.get_category_type1(resp)
        if str(cate_id) == "167"
        else spider.get_category_type2(resp)
    )

    for sub_name, sub_url in sub_cates.items():
        sub_dir = cate_dir / sub_name
        sub_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📁 子类：{sub_name}")
        resp = spider.get_html(sub_url)
        page_count = spider.get_page_count(resp)

        # 收集下载链接
        all_links = {}
        for page in range(1, page_count + 1):
            page_url = f"{sub_url}/default/{page}"
            resp = spider.get_html(page_url)
            download_links = spider.get_download_list(resp)

            if args.recommended:
                download_links = {
                    k: v for k, v in download_links.items() if "官方推荐" in k
                }

            all_links.update(download_links)

        if all_links:
            print(f"📦 共 {len(all_links)} 个词库待下载")
            spider.download_dicts(all_links, sub_dir)

print("\n✅ 所有词库下载完成！")
