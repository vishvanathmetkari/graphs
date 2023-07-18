import pprint
from flask import Flask, render_template,request
import plotly.graph_objects as go
from load_data import *
from plotly.subplots import make_subplots
import plotly

app = Flask(__name__)

template_color = 'plotly_dark'
def get_memory_graph():
    global memory_data
    timestamp = []
    memused = []
    for mem_load in memory_data:
        timestamp.append(mem_load['timestamp']['time'])
        memused.append(mem_load['memory']['memused-percent'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamp, y=memused, name='memory used'))
    # Customize the graph layout
    fig.update_layout(
                    title={'text':'Memory Utilization',
                                'x': 0.5,
                                'y': 0.9,
                                'xanchor': 'center',
                                'yanchor': 'top'
                                },
                      xaxis_title='Time',
                      yaxis_title='Utilization',
                      template=template_color,

    )
    # # Add hover effects to the graph
    fig.update_traces(hovertemplate='Time: %{x}<br><b>Utilization: %{y:.2f}%</b><extra></extra>')
    return fig

def get_disk_graph():
    global disk_data
    timestamps = []
    disk_names = [disk["disk-device"] for disk in disk_data[0]['disk']]
    rkB_values = {disk_name: [] for disk_name in disk_names}
    wkB_values = {disk_name: [] for disk_name in disk_names}
    for data in disk_data:
        timestamp = data['timestamp']['time']
        timestamps.append(timestamp)
        disk = data['disk']
        for disk_stat in disk:
            disk_name = disk_stat['disk-device']
            if disk_name in disk_names:
                rkB = disk_stat['rkB']
                wkB = disk_stat['wkB']
                rkB_values[disk_name].append(rkB)
                wkB_values[disk_name].append(wkB)
    fig = go.Figure()
    for disk_name in disk_names:
        fig.add_trace(go.Scatter(x=timestamps, y=rkB_values[disk_name], mode='lines+markers',name= f"rkB ({disk_name})", meta=f"rkB ({disk_name})"))
        fig.add_trace(go.Scatter(x=timestamps, y=wkB_values[disk_name], mode='lines+markers',name= f"wkB ({disk_name})", meta=f"wkB ({disk_name})"))

    fig.update_layout(  title={'text':'Disk Utilization',
                                'x': 0.5,
                                'y': 0.9,
                                'xanchor': 'center',
                                'yanchor': 'top'
                                },
                      xaxis_title='Time',
                      yaxis_title='Kilobytes',
                       template=template_color,)
    fig.update_traces(hovertemplate='Time: %{x}<br><b>Utilization: %{y:.2f}%</b><br>Disk-Device: %{meta}<extra></extra>')
    return fig

def get_network_graph():
    global network_data
    timestamps = []
    iface_names = [iface_data["iface"] for iface_data in network_data[0]['network']['net-dev']]
    rxkB_values = {iface_name: [] for iface_name in iface_names}
    txkB_values = {iface_name: [] for iface_name in iface_names}
    for data in network_data:
        timestamp = data['timestamp']['time']
        timestamps.append(timestamp)
        net_dev = data['network']['net-dev']
        for iface_data in net_dev:
            iface_name = iface_data['iface']
            if iface_name in iface_names:
                rxkB = iface_data['rxkB']
                txkB = iface_data['txkB']
                rxkB_values[iface_name].append(rxkB)
                txkB_values[iface_name].append(txkB)

    fig = go.Figure()
    for iface_name in iface_names:
        fig.add_trace(go.Scatter(x=timestamps, y=rxkB_values[iface_name], mode='lines+markers', name=f"rxkB ({iface_name})",meta=f"rxkB ({iface_name})"))
        fig.add_trace(go.Scatter(x=timestamps, y=txkB_values[iface_name], mode='lines+markers', name=f"txkB ({iface_name})",meta=f"txkB ({iface_name})"))

    fig.update_layout(  title={'text':'Network Metrics',
                                'x': 0.5,
                                'y': 0.9,
                                'xanchor': 'center',
                                'yanchor': 'top'
                                },
                      xaxis_title='Time',
                      yaxis_title='Kilobytes',
                       template=template_color)
    fig.update_traces(hovertemplate='Time: %{x}<br><b>Utilization: %{y:.2f}%</b><br>iface: %{meta} <extra></extra>')
    return fig

def get_cpu_line_graph():
    global cpu_load_data
    x_values = []
    user_values = []
    nice_values = []
    system_values = []
    iowait_values = []
    steal_values = []
    idle_values = []
    for cpu_load in cpu_load_data:
        timestamp = cpu_load['timestamp']['time']
        x_values.append(timestamp)
        cpu_data = cpu_load['cpu-load'][0]
        user_values.append(cpu_data['user'])
        nice_values.append(cpu_data['nice'])
        system_values.append(cpu_data['system'])
        iowait_values.append(cpu_data['iowait'])
        steal_values.append(cpu_data['steal'])
        idle_values.append(cpu_data['idle'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_values, y=user_values, name='User'))
    fig.add_trace(go.Scatter(x=x_values, y=nice_values, name='Nice'))
    fig.add_trace(go.Scatter(x=x_values, y=system_values, name='System'))
    fig.add_trace(go.Scatter(x=x_values, y=iowait_values, name='IO Wait'))
    fig.add_trace(go.Scatter(x=x_values, y=steal_values, name='Steal'))
    fig.add_trace(go.Scatter(x=x_values, y=idle_values, name='Idle'))
    # Customize the graph layout
    fig.update_layout(
                    title={'text':'CPU Load',
                                'x': 0.5,
                                'y': 0.9,
                                'xanchor': 'center',
                                'yanchor': 'top',
                                },
                      xaxis_title='Time',
                      yaxis_title='Utilization',
                     template=template_color,

    )
    # # Add hover effects to the graph
    fig.update_traces(hovertemplate='Time: %{x}<br><b>Utilization: %{y:.2f}%</b><extra></extra>')
    return fig

def get_cpu_heatmap():
    global cpu_load_data
    x_values = []
    z_values = []
    for data in cpu_load_data:
        x_values.append(data['timestamp']['time'])
        z_values.append([sum([cpu['iowait'], cpu['nice'], cpu['steal'], cpu['system'], cpu['user']]) for cpu in data['cpu-load'] if cpu['cpu'] != 'all'])
    y_values = [cpu['cpu'] for cpu in cpu_load_data[0]['cpu-load'] if cpu['cpu'] != 'all']
    z_values = list(zip(*z_values))
    fig = go.Figure(data=go.Heatmap(
        x=x_values,
        y=y_values,
        z=z_values,
        colorscale='RdYlGn_r',
        xgap=1,
        zmax=100,
        zmin=0,
        ygap=1,
        hoverongaps=False,
        hovertemplate='Time: %{x}<br>CPU: %{y}<br><b>Utilization: %{z}%</b><extra></extra>',

    ))

    fig.update_layout(
        title={    'text':'CPU Utilization',
                    'x': 0.5,
                    'y': 0.9,
                    'xanchor': 'center',
                    'yanchor': 'top'
                    },
        xaxis_title='Time',
        yaxis_title='CPU',
        template=template_color,
    )

    # for i in range(len(z_values)):
    #     for j in range(0,len(x_values)):
    #         fig.add_annotation(
    #             x=j,
    #             y=i,
    #             text=str(z_values[i][j])+"%",
    #             showarrow=False,
    #             font=dict(color='black'),
    #         )

    return fig


def get_graphs(file_key):
    global cpu_load_data,network_data,disk_data,memory_data
    cpu_load_data = get_cpu_load(file_key)
    fig = get_cpu_heatmap()
    plot_html = fig.to_html(full_html=False)
    line_fig = get_cpu_line_graph()
    line_fig_html = line_fig.to_html(full_html=False)
    network_data = get_network_data(file_key)
    network_line_graph = get_network_graph()
    network_line_graphHTML = network_line_graph.to_html(full_html=False)
    disk_data = get_disk_data(file_key)
    disk_line_graph = get_disk_graph()
    disk_line_graphHTML = disk_line_graph.to_html(full_html=False)
    memory_data = get_memory_data(file_key)
    memory_line_graph = get_memory_graph()
    memory_line_graphHTML = memory_line_graph.to_html(full_html=False)
    return plot_html, line_fig_html,network_line_graphHTML ,disk_line_graphHTML, memory_line_graphHTML

@app.route('/display_graph',methods=['GET'])
def display_graph():
    if request.args.get('folder'):
        folder = request.args.get('folder')
        get_inside_files(folder)
    if request.args.get('selected'):
        selected_value = request.args.get('selected')
        plot_html, line_fig_html,network_line_graphHTML ,disk_line_graphHTML, memory_line_graphHTML=get_graphs(selected_value)
        return render_template('display_graph.html',nav_parameters=list(file_path.keys()), cpu_heatmap=plot_html,cpu_line_graph=line_fig_html,network_line_graphHTML=network_line_graphHTML,disk_line_graphHTML=disk_line_graphHTML,memory_line_graphHTML=memory_line_graphHTML,selected_value=selected_value ,json_data =get_results(folder),current_folder=folder)
    else:
        file_key =list(file_path.keys())[0]
        plot_html, line_fig_html,network_line_graphHTML ,disk_line_graphHTML, memory_line_graphHTML=get_graphs(file_key)
        return render_template('display_graph.html',nav_parameters=list(file_path.keys()), cpu_heatmap=plot_html,cpu_line_graph=line_fig_html,network_line_graphHTML=network_line_graphHTML,disk_line_graphHTML=disk_line_graphHTML,memory_line_graphHTML=memory_line_graphHTML,selected_value=file_key,json_data=get_results(folder),current_folder=folder)

@app.route('/')
def index():
    nested_dict = {}
    sub_folders = [name for name in os.listdir(DEFAULT_FOLDER) if os.path.isdir(os.path.join(DEFAULT_FOLDER, name))]
    # print(sub_folders)
    for folder in sub_folders:
        results = get_score(folder)
        nested_dict[folder] = {}
        nested_dict[folder]["score"] = results[0]
        nested_dict[folder]["server_cpu_arch"] = results[1]
    pprint.pprint(nested_dict)
    return render_template('index.html', nested_dict=nested_dict)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
