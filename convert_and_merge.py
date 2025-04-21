#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pathlib
import subprocess
import shutil

# 项目根目录：自动获取当前脚本所在目录
base_dir = pathlib.Path(__file__).resolve().parent

# 构建目录
build_dir = base_dir / "build_fcitx5"
txt_tmp_dir = build_dir / "txt_tmp"
merged_txt_path = build_dir / "merged_final.txt"
final_dict_path = build_dir / "merged_final.dict"

# 创建构建目录和临时目录
txt_tmp_dir.mkdir(parents=True, exist_ok=True)

# 清理旧的合并文件
if merged_txt_path.exists():
    merged_txt_path.unlink()

# Step 1: scel → txt
print("🔁 转换 .scel → .txt")
scel_dir = base_dir / "sogou_scel"
for scel_file in scel_dir.rglob("*.scel"):
    output_txt = txt_tmp_dir / f"{scel_file.stem}.txt"
    subprocess.run(["scel2org5", str(scel_file), "-o", str(output_txt)])

# Step 2: 合并所有 txt 文件
print("📦 合并所有 .txt 文件")
with open(merged_txt_path, "w", encoding="utf-8") as merged_file:
    for txt_file in sorted(txt_tmp_dir.glob("*.txt")):
        with open(txt_file, "r", encoding="utf-8") as f:
            merged_file.write(f.read())
            merged_file.write("\n")

# Step 3: 合并后的 txt → .dict
print("⚙️ 生成 .dict 文件")
subprocess.run(["libime_pinyindict", str(merged_txt_path), str(final_dict_path)])

# Step 4: 清理 txt_tmp 临时目录
print("🧹 清理临时文件")
shutil.rmtree(txt_tmp_dir)

print(f"✅ 完成！生成的 .dict 文件位于：{final_dict_path}")
