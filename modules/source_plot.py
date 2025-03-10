import pandas as pd
import matplotlib.pyplot as plt  # 新增必要库

from vector_service import vector_store  # 根据实际导入方式调整

# 连接数据库（示例使用本地客户端）
collection = vector_store._collection

# 获取元数据并转为DataFrame
data = collection.get()
df = pd.DataFrame({
    "id": data["ids"],
    "document": data["documents"],
    "metadata": data["metadatas"]
})

# 统计文档来源分布
source_counts = df["metadata"].apply(lambda x: x.get("source")).value_counts()

# 可视化设置
plt.figure(figsize=(12, 6))
source_counts.plot(kind="bar",
                  title="source distribution",
                  xlabel="source",
                  ylabel="count",
                  rot=45)  # 旋转X轴标签

# 显示图表
plt.tight_layout()  # 自动调整布局
plt.show()