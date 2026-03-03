"""
文件处理器模块 - 负责结果文件的增量写入
"""
import os
from datetime import datetime


class FileHandler:
    """文件处理器 - 负责结果文件的增量写入"""
    
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名 fireworks_YYYYMMDD.txt
        today = datetime.now().strftime("%Y%m%d")
        self.results_file = os.path.join(output_dir, f"fireworks_{today}.txt")
    
    def save_account(self, data: dict):
        """保存账号信息（增量写入）"""
        # 构建输出内容
        lines = [
            "",
            "  项目         验证结果",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"  邮箱         {data.get('email', 'N/A')}",
            f"  密码         {data.get('password', 'N/A')}",
            f"  API Key      {data.get('api_key', 'N/A')}",
            f"  Account ID   {data.get('account_id', 'N/A')}",
            "",
            f"  注册时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]
        
        content = "\n".join(lines)
        
        # 追加写入文件
        mode = "a" if os.path.exists(self.results_file) else "w"
        with open(self.results_file, mode, encoding="utf-8") as f:
            if mode == "w":
                # 首次写入添加标题
                f.write("Fireworks AI 账号注册结果\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n")
            f.write(content + "\n")
        
        print(f"[FileHandler] 结果已保存到: {self.results_file}")
