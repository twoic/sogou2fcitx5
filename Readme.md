# 🐍 Sogou-to-Fcitx5 - 搜狗拼音词库批量下载与转换工具

[![Language](https://img.shields.io/badge/Language-Python-blue.svg)](https://www.python.org)

> 把人类从重复的劳动中解放出来，去创造新的事物。

---

## 📖 项目简介

本项目用于 **批量自动下载搜狗拼音词库** 并 **转换为 Fcitx5 输入法可用的 `.dict` 文件**，适用于 Linux 用户、高级输入法使用者、NLP 工程师等。

---

## ✨ 功能特性

- 🚀 自动测速、智能分配多线程下载
- 📥 多线程并发 + 下载进度条
- 🔁 支持断点续传 + 自动重试
- 🧼 文件命名清洗，避免非法字符
- 🎯 支持只下载“官方推荐”词库
- 🔄 一键批量转换 `.scel → .txt → .dict`
- 🈶 可直接导入至 `fcitx5-pinyin`

---

## 🧱 环境准备

### ✅ 1. 安装系统依赖（用于词库格式转换）

```
sudo apt update
sudo apt install fcitx5-chinese-addons
```

✅ 提供 scel2org5 与 libime_pinyindict 转换工具

✅ 2. 安装 Python & pip 依赖
```
如果未安装 pip3：
sudo apt install python3-pip
```
```
安装项目依赖：
pip install -r requirements.txt
```

🚀 使用步骤（完全复制粘贴即可）
✅ 1. 克隆项目

```
git clone https://github.com/twoic/sogou2fcitx5.git

cd sogou2fcitx5
```
✅ 2. 下载词库
```
python3 main.py
可选参数：

参数	说明
--recommended	只下载“官方推荐”词库
--workers 20	手动设定下载线程数（默认自动）
--categories 1 132	仅下载指定分类（可多个）
示例：


python3 main.py --recommended --categories 1 132
```

✅ 3. 批量转换词库为 Fcitx5 格式

```
python3 convert_and_merge.py
```

### 输出文件为：
- build_fcitx5/merged_final.dict


✅ 4. 导入到 Fcitx5 输入法

```
mkdir -p ~/.local/share/fcitx5/pinyin/dictionaries
cp build_fcitx5/merged_final.dict ~/.local/share/fcitx5/pinyin/dictionaries/
```
- 重启输入法或重新加载词典即可使用！

## 📁 项目结构说明

sogou2fcitx5/  
├── `main.py`                   # 主程序：启动下载  
├── `sougou_downloader.py`      # 多线程下载逻辑（支持测速、重试）  
├── `convert_and_merge.py`      # 词库转换脚本  
├── `release_cleaner.py`        # 自动清理 + 打包脚本  
├── `sogou_scel/`               # 下载的 `.scel` 词库（自动生成）  
├── `build_fcitx5/`             # 最终生成的 `.dict` 文件  
├── `README.md`  
└── `LICENSE`  

---

## 🧾 分类 ID 对照表

| 分类名称     | ID   |
| ------------ | ---- |
| 城市信息     | 167  |
| 自然科学     | 1    |
| 社会科学     | 76   |
| 工程应用     | 96   |
| 农林渔畜     | 127  |
| 医学医药     | 132  |
| 电子游戏     | 436  |
| 艺术设计     | 154  |
| 生活百科     | 389  |
| 运动休闲     | 367  |
| 人文科学     | 31   |
| 娱乐休闲     | 403  |




