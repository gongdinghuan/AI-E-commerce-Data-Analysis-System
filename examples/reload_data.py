"""
重新导入数据到数据库

@Author: gongdinghuan
@Date: 2026-01-30
@Description: 从CSV文件重新导入数据到数据库
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_manager import DataManager

def reload_data():
    """重新导入数据"""
    print("=" * 60)
    print("🔄 重新导入数据到数据库")
    print("=" * 60)
    
    dm = DataManager()
    
    print(f"\n📂 数据库路径: {dm.db_path}")
    print(f"📁 数据目录: {Path(__file__).parent.parent / 'data'}")
    
    print("\n🗑️  清空现有数据...")
    try:
        dm.conn.execute("DELETE FROM users")
        dm.conn.execute("DELETE FROM products")
        dm.conn.execute("DELETE FROM orders")
        dm.conn.execute("DELETE FROM funnel")
        print("  ✅ 已清空所有表")
    except Exception as e:
        print(f"  ❌ 清空失败: {e}")
        return False
    
    print("\n📥 导入新数据...")
    success = dm.load_csv_to_db(force_reload=True)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 数据导入完成！")
        print("=" * 60)
        
        stats = dm.get_table_stats()
        print(f"\n📊 当前数据库统计：")
        print(f"   用户数: {stats['users']}")
        print(f"   商品数: {stats['products']}")
        print(f"   订单数: {stats['orders']}")
        print(f"   漏斗数据: {stats['funnel']}")
        return True
    else:
        print("\n❌ 数据导入失败！")
        return False

if __name__ == "__main__":
    reload_data()
