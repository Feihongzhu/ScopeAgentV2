"""
作业统计信息解析器 - 解析JobStatistics.xml文件
"""

import xml.etree.ElementTree as ET


def parse_job_statistics_xml(file_path: str) -> str:
    """解析 JobStatistics.xml 文件"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        summary = ["作业统计信息:"]
        
        job_id = root.find('JobId')
        if job_id is not None:
            summary.append(f"- 作业ID: {job_id.text}")
        
        # 整体统计
        overall_stats = root.find('OverallStatistics')
        if overall_stats is not None:
            summary.append("- 整体统计:")
            for child in overall_stats:
                summary.append(f"  {child.tag}: {child.text}")
        
        # Stage统计
        stage_stats = root.find('StageStatistics')
        if stage_stats is not None:
            summary.append("- Stage统计:")
            for stage in stage_stats.findall('Stage'):
                stage_id = stage.find('StageId')
                stage_name = stage.find('StageName')
                duration = stage.find('Duration')
                
                stage_info = f"  Stage {stage_id.text if stage_id is not None else 'Unknown'}"
                if stage_name is not None:
                    stage_info += f" ({stage_name.text})"
                if duration is not None:
                    stage_info += f" - 耗时: {duration.text}"
                
                summary.append(stage_info)
                
                # 检查倾斜任务
                skewed_tasks = stage.find('SkewedTasks')
                if skewed_tasks is not None:
                    tasks = skewed_tasks.findall('Task')
                    if tasks:
                        summary.append(f"    检测到 {len(tasks)} 个倾斜任务")
                        for task in tasks[:3]:  # 只显示前3个
                            task_id = task.find('TaskId')
                            skew_reason = task.find('SkewReason')
                            if task_id is not None and skew_reason is not None:
                                summary.append(f"    - {task_id.text}: {skew_reason.text}")
        
        # 性能指标
        performance_metrics = root.find('PerformanceMetrics')
        if performance_metrics is not None:
            summary.append("- 性能指标:")
            for metric in performance_metrics.findall('Metric'):
                name = metric.find('Name')
                value = metric.find('Value')
                status = metric.find('Status')
                
                if name is not None and value is not None:
                    metric_info = f"  {name.text}: {value.text}"
                    if status is not None and status.text == "Exceeded":
                        metric_info += " (超出阈值)"
                    summary.append(metric_info)
        
        return "\n".join(summary)
    except Exception as e:
        return f"解析JobStatistics.xml失败: {str(e)}" 