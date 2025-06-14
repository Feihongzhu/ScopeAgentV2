"""
数据流图解析器 - 解析__DataMapDfg__.json文件  
"""

import json


def parse_data_flow_graph_json(file_path: str) -> str:
    """解析 __DataMapDfg__.json 数据流图文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = ["数据流图信息:"]
        
        if 'vertices' in data:
            vertices = data['vertices']
            summary.append(f"- 顶点数: {len(vertices)}")
            
            # 统计顶点类型
            vertex_types = {}
            for vertex in vertices:
                vertex_type = vertex.get('type', 'Unknown')
                vertex_types[vertex_type] = vertex_types.get(vertex_type, 0) + 1
            
            summary.append("- 顶点类型分布:")
            for v_type, count in vertex_types.items():
                summary.append(f"  {v_type}: {count}")
        
        if 'edges' in data:
            edges = data['edges']
            summary.append(f"- 边数: {len(edges)}")
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析数据流图文件失败: {str(e)}" 