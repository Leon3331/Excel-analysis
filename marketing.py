import os
import pandas as pd
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # 允许跨域请求，便于前后端分离开发

# 配置上传文件夹和允许的文件扩展名
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 文件大小限制

# 全局变量存储处理后的数据
monitor_data = None
last_month_data = None  # 存储上个月最后一天的数据

# 默认异常阈值（百分比）
abnormal_threshold = 10


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_date_from_column_name(col_name):
    """从列名中提取日期信息"""
    if pd.isna(col_name):
        return None

    col_str = str(col_name)

    # 匹配模式：数字+日 或 气量-数字日
    match = re.search(r'(\d+)日', col_str)
    if match:
        return int(match.group(1))

    # 匹配"气量-1日"格式
    match = re.search(r'气量-(\d+)日', col_str)
    if match:
        return int(match.group(1))

    return None


def convert_to_serializable(obj):
    """将对象转换为可JSON序列化的格式"""
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj


def find_sequence_column(df):
    """查找序号列"""
    for col in df.columns:
        if str(col).strip() in ['序号', '编号', 'ID']:
            return col
    return None


def find_category_column(df):
    """查找分类列"""
    for col in df.columns:
        if str(col).strip() == '分类':
            return col
    return None


@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    """分析月用气监控表数据"""
    global monitor_data, last_month_data, abnormal_threshold

    # 检查是否有文件部分
    if 'main_file' not in request.files:
        return jsonify({'error': '没有主文件部分'}), 400

    main_file = request.files['main_file']

    # 检查是否选择了文件
    if main_file.filename == '':
        return jsonify({'error': '未选择主文件'}), 400

    # 获取参数
    threshold = request.form.get('threshold', abnormal_threshold)
    analysis_date = request.form.get('analysis_date')

    try:
        abnormal_threshold = float(threshold)

        # 解析日期
        if analysis_date:
            analysis_date_obj = datetime.strptime(analysis_date, '%Y-%m-%d')
            current_day = analysis_date_obj.day
            is_first_day = current_day == 1
        else:
            return jsonify({'error': '未提供分析日期'}), 400

    except ValueError:
        return jsonify({'error': '参数格式错误'}), 400

    # 如果是第一天，检查是否有月度补充文件
    if is_first_day:
        if 'extra_file' not in request.files:
            return jsonify({'error': '每月1号需要上传月度补充文件'}), 400

        extra_file = request.files['extra_file']
        if extra_file.filename == '':
            return jsonify({'error': '未选择月度补充文件'}), 400
    else:
        extra_file = None

    # 保存并处理主文件
    if main_file and allowed_file(main_file.filename):
        main_filename = secure_filename(main_file.filename)
        main_filepath = os.path.join(app.config['UPLOAD_FOLDER'], main_filename)
        main_file.save(main_filepath)

        try:
            # 读取Excel文件
            df = pd.read_excel(main_filepath)

            # 查找序号列
            sequence_col = find_sequence_column(df)
            if sequence_col is None:
                return jsonify({'error': '未找到"序号"列'}), 400

            # 查找分类列
            category_col = find_category_column(df)

            # 查找包含日期的列
            date_columns = []

            for col in df.columns:
                # 检查是否是日期列
                if extract_date_from_column_name(col) is not None:
                    date_columns.append(col)

            if not date_columns:
                return jsonify({'error': '未找到日期列（格式应为"X日"或"气量-X日"）'}), 400

            # 按日期排序列
            date_columns_sorted = sorted(
                date_columns,
                key=lambda x: extract_date_from_column_name(x) or 0
            )

            # 获取当前日期的气量列（万立方米）
            current_col = next((c for c in date_columns_sorted if extract_date_from_column_name(c) == current_day),
                               None)
            if not current_col:
                return jsonify({'error': f'未找到{current_day}日的气量列'}), 400

            # 获取前一天的气量列
            if is_first_day:
                # 如果是第一天，需要处理月度补充文件
                if extra_file and allowed_file(extra_file.filename):
                    extra_filename = secure_filename(extra_file.filename)
                    extra_filepath = os.path.join(app.config['UPLOAD_FOLDER'], extra_filename)
                    extra_file.save(extra_filepath)

                    try:
                        # 读取月度补充文件
                        extra_df = pd.read_excel(extra_filepath)

                        # 查找序号列
                        extra_sequence_col = find_sequence_column(extra_df)
                        if extra_sequence_col is None:
                            return jsonify({'error': '月度补充文件中未找到"序号"列'}), 400

                        # 查找分类列
                        extra_category_col = find_category_column(extra_df)

                        # 查找包含日期的列
                        extra_date_columns = []

                        for col in extra_df.columns:
                            # 检查是否是日期列
                            if extract_date_from_column_name(col) is not None:
                                extra_date_columns.append(col)

                        if not extra_date_columns:
                            return jsonify({'error': '月度补充文件中未找到日期列'}), 400

                        # 按日期排序列
                        extra_date_columns_sorted = sorted(
                            extra_date_columns,
                            key=lambda x: extract_date_from_column_name(x) or 0
                        )

                        # 获取上个月最后一天的数据列（通常是31日）
                        prev_col = extra_date_columns_sorted[-1] if extra_date_columns_sorted else None
                        if not prev_col:
                            return jsonify({'error': '月度补充文件中未找到最后一天的数据列'}), 400

                        # 获取合计行的前一天气量
                        if extra_category_col and extra_category_col in extra_df.columns:
                            # 如果有分类列，使用分类列
                            prev_gas_rows = extra_df[extra_df[extra_category_col] == '合计']
                        else:
                            # 如果没有分类列，使用序号列（假设序号为999的是合计行）
                            prev_gas_rows = extra_df[extra_df[extra_sequence_col] == 999]

                        if prev_gas_rows.empty:
                            return jsonify({'error': '月度补充文件中未找到"合计"行'}), 400

                        # 存储上个月的数据
                        last_month_data = {}
                        for _, row in prev_gas_rows.iterrows():
                            row_id = row[extra_sequence_col]
                            last_month_data[row_id] = row[prev_col]

                    except Exception as e:
                        return jsonify({'error': f'处理月度补充文件时出错: {str(e)}'}), 500
                else:
                    return jsonify({'error': '月度补充文件无效'}), 400
            else:
                # 如果不是第一天，从主文件中获取前一天的数据列
                prev_day = current_day - 1
                prev_col = next((c for c in date_columns_sorted if extract_date_from_column_name(c) == prev_day), None)

                if not prev_col:
                    return jsonify({'error': f'未找到{prev_day}日的气量列'}), 400

            # 获取合计行
            if category_col and category_col in df.columns:
                # 如果有分类列，使用分类列
                total_rows = df[df[category_col] == '合计']
            else:
                # 如果没有分类列，使用序号列（假设序号为999的是合计行）
                total_rows = df[df[sequence_col] == 999]

            if total_rows.empty:
                return jsonify({'error': '未找到"合计"行'}), 400

            # 处理数据
            processed_data = []
            abnormal_records = []
            total_current_gas = 0
            total_prev_gas = 0

            for _, row in total_rows.iterrows():
                row_id = row[sequence_col]
                row_name = row.get('客户名称', f"合计行{row_id}")

                # 获取当前天气量
                current_gas = row[current_col]
                current_gas = convert_to_serializable(current_gas)
                total_current_gas += current_gas if current_gas is not None else 0

                # 获取前一天的气量
                if is_first_day:
                    # 如果是第一天，从月度补充文件中获取前一天的气量
                    prev_gas = last_month_data.get(row_id, 0)
                else:
                    # 如果不是第一天，从主文件中获取前一天的气量
                    prev_gas = row[prev_col] if prev_col in row else 0

                prev_gas = convert_to_serializable(prev_gas)
                total_prev_gas += prev_gas if prev_gas is not None else 0

                # 计算变化量和变化率
                change = current_gas - prev_gas if current_gas is not None and prev_gas is not None else None
                change_rate = (change / prev_gas) * 100 if change is not None and prev_gas != 0 else None
                is_abnormal = abs(change_rate) > abnormal_threshold if change_rate is not None else False

                # 转换为可序列化的格式
                change = convert_to_serializable(change)
                change_rate = convert_to_serializable(change_rate)
                is_abnormal = convert_to_serializable(is_abnormal)

                record = {
                    '序号': row_id,
                    '名称': row_name,
                    '日期': f"{current_day}日",
                    '气量(万立方米)': current_gas,
                    '前一天气量(万立方米)': prev_gas,
                    '变化量(万立方米)': change,
                    '变化率(%)': f"{change_rate}%" if change_rate is not None else None,
                    '异常': is_abnormal
                }

                processed_data.append(record)

                # 只记录异常数据
                if is_abnormal:
                    abnormal_records.append(record)

            # 存储处理后的数据
            monitor_data = processed_data

            # 转换为可序列化的格式
            for record in abnormal_records:
                for key in record:
                    record[key] = convert_to_serializable(record[key])

            # 生成分析报告
            result_text = f"""=== 数据分析报告 ===
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

分析参数:
├── 异常阈值: {abnormal_threshold}%
├── 分析日期: {analysis_date}
├── 主文件: {main_filename}
"""

            if is_first_day and extra_file:
                result_text += f"└── 月度文件: {extra_filename}\n\n"
            else:
                result_text += "└── 月度文件: 不需要\n\n"

            result_text += "分析过程:\n"
            result_text += "├── 正在读取文件数据... ✓\n"
            result_text += "├── 正在解析数据格式... ✓\n"
            result_text += "├── 查找合计行数据... ✓\n"
            result_text += "├── 计算气量变化... ✓\n"
            result_text += "└── 生成分析报告... ✓\n\n"

            result_text += f"分析结果 (阈值 {abnormal_threshold}%):\n"
            result_text += f"├── 当日总气量: {total_current_gas} 万立方米\n"
            result_text += f"├── 前日总气量: {total_prev_gas} 万立方米\n"
            result_text += f"├── 总变化量: {total_current_gas - total_prev_gas} 万立方米\n"
            result_text += f"├── 总变化率: {(total_current_gas - total_prev_gas) / total_prev_gas * 100 if total_prev_gas != 0 else 0}%\n"
            result_text += f"└── 异常数据数量: {len(abnormal_records)}\n\n"

            if abnormal_records:
                result_text += "异常数据详情:\n"
                for record in abnormal_records:
                    result_text += f"├── {record['名称']}: {record['气量(万立方米)']} → {record['前一天气量(万立方米)']} (变化: {record['变化量(万立方米)']}, 变化率: {record['变化率(%)']})\n"
                result_text += "\n"

            result_text += "建议操作:\n"
            result_text += "├── 查看详细报告\n"
            result_text += "├── 导出分析结果\n"
            result_text += "└── 调整阈值重新分析\n"

            return jsonify({
                'message': '数据分析成功',
                'result_text': result_text,
                'abnormal_threshold': abnormal_threshold,
                'abnormal_count': len(abnormal_records),
                'abnormal_records': abnormal_records,
                'total_current_gas': total_current_gas,
                'total_prev_gas': total_prev_gas,
                'data': monitor_data
            })

        except Exception as e:
            return jsonify({'error': f'处理文件时出错: {str(e)}'}), 500

    return jsonify({'error': '文件类型不允许'}), 400


@app.route('/api/update_threshold', methods=['POST'])
def update_threshold():
    """更新异常检测阈值"""
    global abnormal_threshold, monitor_data

    new_threshold = request.json.get('threshold')

    if new_threshold is None:
        return jsonify({'error': '未提供阈值参数'}), 400

    try:
        abnormal_threshold = float(new_threshold)

        # 如果已经有监控数据，重新计算异常
        if monitor_data is not None:
            # 重新计算异常
            for record in monitor_data:
                if record['变化量(万立方米)'] is not None and record['前一天气量(万立方米)'] is not None:
                    change_rate = (record['变化量(万立方米)'] / record['前一天气量(万立方米)']) * 100 if record[
                                                                                             '前一天气量(万立方米)'] != 0 else float(
                        'inf')
                    record['异常'] = abs(change_rate) > abnormal_threshold
                    record['变化率(%)'] = f"{change_rate}%"

            # 获取异常数据
            abnormal_records = [record for record in monitor_data if record['异常']]

            # 转换为可序列化的格式
            for record in abnormal_records:
                for key in record:
                    record[key] = convert_to_serializable(record[key])

            return jsonify({
                'message': '阈值更新成功',
                'abnormal_threshold': abnormal_threshold,
                'abnormal_count': len(abnormal_records),
                'abnormal_records': abnormal_records
            })
        else:
            return jsonify({
                'message': '阈值更新成功',
                'abnormal_threshold': abnormal_threshold
            })

    except ValueError:
        return jsonify({'error': '阈值参数格式错误'}), 400


@app.route('/api/get_data', methods=['GET'])
def get_data():
    """获取当前存储的数据"""
    # 转换为可序列化的格式
    monitor_data_serializable = []
    if monitor_data:
        for record in monitor_data:
            serializable_record = {}
            for key, value in record.items():
                serializable_record[key] = convert_to_serializable(value)
            monitor_data_serializable.append(serializable_record)

    return jsonify({
        'monitor_data': monitor_data_serializable,
        'last_month_data': convert_to_serializable(last_month_data),
        'abnormal_threshold': abnormal_threshold
    })


@app.route('/api/clear_data', methods=['POST'])
def clear_data():
    """清除所有数据"""
    global monitor_data, last_month_data

    monitor_data = None
    last_month_data = None

    return jsonify({'message': '所有数据已清除'})


if __name__ == '__main__':
    # 确保上传文件夹存在
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(debug=True, port=5000)