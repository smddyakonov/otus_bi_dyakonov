# ИМПОРТЫ
#import json
#import plotly.express as px
#import plotly.graph_objects as go
#from plotly.subplots import make_subplots

import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, ctx, dash_table
import dash_bootstrap_components as dbc

from def_graphfunc import print_treemap_jbjem_ee, print_create_pie_charts, print_create_boxplot, \
    print_create_line_plot, create_consumption_bar_chart, create_histogram_with_boxplot, print_network_power, \
    calculate_network_power, create_mapbox_scatter_point

from def_get_xlsx import get_xlsx

# ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ И ЗАГРУЗКА ДАННЫХ
app = Dash(__name__,
           external_stylesheets=[
               dbc.themes.BOOTSTRAP,
               'assets/css/project.css',
               'assets/css/typography.css'],
           suppress_callback_exceptions=True
           )

geojson_file = r'coords_object.geojson'

file = r'часы РРЭ.xlsx'
df_pnr = get_xlsx(file = file, parse_flag=True, sheet_name='rph', header_row=0)
df_ppn = get_xlsx(file = file, parse_flag=True, sheet_name='phpn', header_row=0)

file = r'df_data_ee_crop.xlsx'
df_data = get_xlsx(file=file, parse_flag=True, sheet_name='Sheet1', header_row=0)

df_data['year'] = df_data['date'].dt.year
df_data['month'] = df_data['date'].dt.month
df_data['hour'] = df_data['date'].dt.hour

# Дата начало-конец периода
min_date = df_data['date'].min()
max_date = df_data['date'].max()

# Начало-конец слайдера
rent_max = df_data['hour'].max()
rent_min = df_data['hour'].min()

# Канал Объектов
sales_options = [{'value':col,'label':col} for col in df_data['id_Объект'].unique().tolist()]

# Ур. напряж. расч
district_options = [{'value':col,'label':col} for col in df_data['Ур. напряж. расч.'].unique().tolist()]

# Динамические колонки таблицы
columns_options = [{'value':col,'label':col} for col in df_data.columns]

# ЭЛЕМЕНТЫ

sales_channel = dcc.Dropdown(
    id='sales_channel',
    options=sales_options,
    value=[],
    clearable=False,
    placeholder='Выберите объект',
    multi=True
)

rentable_slider = dcc.RangeSlider(
    id='rent_slider',
    min=rent_min,
    max=rent_max,
    value=[rent_min,rent_max],
    dots=False,
    tooltip={"placement": "bottom", "always_visible": True}
)

date_range = dcc.DatePickerRange(
    id='data_filter',
    display_format='DD-MM-YYYY',
    min_date_allowed=min_date,
    max_date_allowed=max_date,
    start_date=min_date,
    end_date=max_date)

accept_button = dbc.Button('Выполнить',id='accept_button',n_clicks=0,className='me-1',color='warning')

district_dropdown = dcc.Dropdown(
    id='district_dropdown',
    options=district_options,
    value=[],
    clearable=True,
    placeholder='Все уровни напряжения',
    multi=False
)

district_school_dropdown = dcc.Dropdown(
    id='district_dropdown_for_api',
    options=sales_options,
    value=[],
    clearable=True,
    placeholder='Уровень напряжения',
    multi=False
)

columns_channel = dcc.Dropdown(
    id='columns_channel',
    options=columns_options,
    value=[],
    clearable=False,
    placeholder='Выберите колонки',
    multi=True
)

# ВЁРСТКА
app.title = 'OTUS DASH'

graph_with_filters = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H6("Объекты")),
                dbc.CardBody(html.Div(sales_channel))])),
            dbc.Col(dbc.Card([
                dbc.CardHeader([html.H6("Часы суток")]),
                dbc.CardBody(html.Div(rentable_slider))])),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H6("Временной период")),
                dbc.CardBody(html.Div(date_range))]))
        ]),
        dbc.Row([
            dbc.Col(accept_button),
            dbc.Col()
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H4('Объемы'),
            dbc.Row(dcc.Graph(id='product_bar'))
        ]),
        dbc.Col([
            html.H4("Объемы в разере суток"),
            dbc.Row(dcc.Graph(id='histogram'))
        ])
    ]),
    dbc.Row([
        html.H4("Динамика объема по месяцам"),
        dcc.Graph(id='line_order')
    ]),
    dbc.Container([
        dbc.Row([
            dbc.Card([
                dbc.CardHeader(dbc.Row(html.H6('Выберите уровень напряжения'))),
                dbc.CardBody(dbc.Row(html.Div(district_dropdown)))
            ]),
            dbc.Row(html.Div(id='change_graph'))
        ])
    ])


])

graph_without_filters = html.Div([
    dbc.Row(
        html.Div([
            html.H4('Иерархия потребления по объектам и уровням напряжения'),
            dcc.Graph(figure=print_treemap_jbjem_ee(df_data))
        ])
    ),
    dbc.Container([
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.H4('Распределение доли по уровням напряжения по объектам'),
                    dcc.Graph(figure=print_create_boxplot(df_data=df_data))
                ])
            ),
            dbc.Col(
                html.Div([
                    html.H4('Доля объемов по уровням напряжения'),
                    dcc.Graph(figure=print_create_pie_charts(df_data=df_data))
                ])
            )
        ])
    ])
])

config_1 = {
        "modeBarButtonsToAdd": [
            "drawline",
            "drawopenpath",
            "drawclosedpath",
            "drawcircle",
            "drawrect",
            "eraseshape",
        ]
    }

maps = html.Div([
    dbc.Row(
        html.Div([
            html.H4('Распределение объектов на карте'),
            dcc.Graph(figure=create_mapbox_scatter_point(geojson_file=geojson_file),config=config_1)
        ])
    ),
])

table = html.Div([
    dbc.Row([
            columns_channel,
            html.Div(id='table_with_filters')
        ])
])

app.layout = dbc.Container(
    html.Div([
    #     HEADER
        html.Div(
            dbc.Row([
                dbc.Col(html.Img(
                    src=app.get_asset_url("images/logo_black.png"),
                    style={'width':'300px','margin-top':'10px','margin-bottom':'10px'}),
                style={'width':'300px'}),
                dbc.Col(html.Div(html.H1('Мониторинг и анализа потребления электроэнергии на производстве'),
                                 style={'margin-left': '-200px'}))]), className='app-header'
        ),
    # BODY
        html.Div([
            dbc.Card([
                dbc.CardHeader(
                    dbc.Tabs([
                        dbc.Tab(label='Мониторинг потребления ЭЭ', tab_id='graph_with_filters'),
                        dbc.Tab(label='Анализ потребления ЭЭ', tab_id='graph_without_filters'),
                        dbc.Tab(label='Картографическая информация', tab_id='maps'),
                        dbc.Tab(label='Таблица', tab_id='table'),
                    ],
                        id='card-tabs',
                        active_tab='graph_with_filters')),
                dbc.CardBody(html.Div(id='card-content'))
            ]),
        ]),
    # FOOTER
        html.Div(
            dbc.Row([
                dbc.Col(html.Img(src=app.get_asset_url("images/logo-small_black.png"),style={'width':'200px'})),
                dbc.Col(html.Div(html.H3('OTUS. Курс «BI-аналитика»')),align='center'),
                dbc.Col(html.P("Дьяконов Семен, 2024 г.")),
        ],align='center'),
        className='app-footer')
    ])
)

# CALLBACK'S (ФУНКЦИИ ОБРАТНОГО ВЫЗОВА)

@app.callback(
    Output(component_id='card-content',component_property='children'),
    Input(component_id='card-tabs',component_property='active_tab')
)
def tab_content(active_tab):
    if active_tab == 'graph_with_filters':
        return graph_with_filters
    if active_tab == 'graph_without_filters':
        return graph_without_filters
    if active_tab == 'maps':
        return maps
    if active_tab == 'table':
        return table

@app.callback(
    Output(component_id='product_bar',component_property='figure'),
    Input(component_id='accept_button',component_property='n_clicks'),
    State(component_id='sales_channel',component_property='value'),
    State(component_id='data_filter',component_property='start_date'),
    State(component_id='data_filter',component_property='end_date'),
    State(component_id='rent_slider',component_property='value')
)

def sales_channel_filter(n_clicks, value_sales_channel, start_date, end_date, range_value):

    if bool(value_sales_channel):
        f_data = df_data.copy(deep=True)
        f_data = f_data[f_data['id_Объект'].isin(value_sales_channel)]
    else:
        f_data = df_data.copy(deep=True)
        value_sales_channel = f_data['id_Объект'].value_counts().index.to_list()

    f_data = f_data[(f_data['hour'] >= range_value[0]) & (f_data['hour'] <= range_value[-1])]

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    f_data = f_data[(f_data['date'] >= start_date) & (f_data['date'] <= end_date)]

    return  create_consumption_bar_chart(df_data=df_data, df_pnr=df_pnr, id_object = value_sales_channel)

@app.callback(
    Output(component_id='histogram',component_property='figure'),
    Input(component_id='rent_slider',component_property='value')
)
def one_filter_renta(range_value):
    f_data = df_data.copy(deep=True)
    f_data = f_data[(f_data['hour'] >= range_value[0]) & (f_data['hour'] <= range_value[-1])]
    return create_histogram_with_boxplot(f_data)

@app.callback(
    Output(component_id='change_graph',component_property='children'),
    Input(component_id='district_dropdown',component_property='value')
)
def sales_bar_by_district(value):

    f_data = calculate_network_power(df_data, df_ppn, df_pnr)

    if ctx.triggered[0]['value'] is None:
        return html.Div([
            html.H4('Сетевая по уровням напряжения'),
            dcc.Graph(figure=print_network_power(f_data, type_layout='Ур. напряж. расч.'))])
    else:
        f_data = f_data[f_data['Ур. напряж. расч.'].isin([value])].reset_index(drop=True)
        return html.Div([
            html.H4('Сетевая по объектам'),
            dcc.Graph(figure=print_network_power(f_data, type_layout='id_Объект'))])

@app.callback(
    Output(component_id='line_order',component_property='figure'),
    Input(component_id='sales_channel',component_property='value'),
    Input(component_id='data_filter',component_property='start_date'),
    Input(component_id='data_filter',component_property='end_date')
)
def sales_dynamic_my_month(value_sales_channel,start_date, end_date):

    if bool(value_sales_channel):
        f_data = df_data.copy(deep=True)
        f_data = f_data[f_data['id_Объект'].isin(value_sales_channel)]
    else:
        f_data = df_data.copy(deep=True)
        value_sales_channel = f_data['id_Объект'].value_counts().index.to_list()

    f_data = f_data[(f_data['date'] >= start_date) & (f_data['date'] <= end_date)]

    f_data['date_month'] = f_data['date'].dt.to_period('M')
    f_data['date_month'] = f_data['date_month'].astype(str)
    data_grouped = f_data.groupby('date_month')['value'].sum().reset_index()

    return print_create_line_plot(f_data, column='id_Объект', id_value=value_sales_channel)

@app.callback(
    Output(component_id='school_api_dropdown',component_property='children'),
    Input(component_id='district_dropdown_for_api',component_property='value')
)
def print_api_dropdown(value):
    f_data = df_data.copy(deep=True)

    f_data = f_data[f_data['Ур. напряж. расч.'].isin([value])]

    school_option = [{'value': col, 'label': col} for col in f_data['id_Объект'].unique().tolist()]

    school_dropdown = dcc.Dropdown(
        id='school_dropdown',
        options=school_option,
        value=[],
        clearable=True,
        placeholder='Объект',
        multi=False)

    if ctx.triggered[0]['value'] is None:
        return ''

    return school_dropdown


@app.callback(
    Output(component_id='table_with_filters',component_property='children'),
    Input(component_id='columns_channel',component_property='value')
)
def table_constructor(value):

    if (len(value) == 0):
        return ''
    if value is None:
        return ''

    f_data = df_data.copy(deep=True)
    f_data = f_data[value]

    element = dash_table.DataTable(
        data=f_data.to_dict('records'),
        columns=[{'name':i,'id':i} for i in f_data.columns],
        page_size=25)

    return element

# ЗАПУСК ПРИЛОЖЕНИЯ

if __name__ == '__main__':
    app.run_server(debug=True, port=8053)