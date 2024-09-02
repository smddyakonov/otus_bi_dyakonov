import json
import folium
import pandas as pd
from dash import dcc

import requests
import imageio.v3 as iio
import io

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

TEMPLATE_FONT_LEGEND = go.layout.Template(
    layout={
       "legend" : {
           'orientation':'h',
           'title_text':''
       },
        'title_font':{
            'family':'ArrialNarrow',
            'size':24
        },
    }
)

TEMPLATE_FONT = go.layout.Template(
    layout={
        'title_font':{
            'family':'ArrialNarrow',
            'size':24
        },
    }
)

#HW
#Иерархия потребления по объектам и уровням напряжения
def print_treemap_jbjem_ee(df_data, year=None, month=None, hour=None):
    if year is None:
        year_list = list(df_data['date'].dt.year.unique())
    else:
        # Инициализация списка
        year_list = []
        # Добавление year в year_list
        if isinstance(year, list):
            year_list.extend(year)
        else:
            year_list.append(year)

    if month is None:
        month_list = list(df_data['date'].dt.month.unique())
    else:
        # Инициализация списка
        month_list = []
        # Добавление month в month_list
        if isinstance(month, list):
            month_list.extend(month)
        else:
            month_list.append(month)

    if hour is None:
        hour_list = list(df_data['date'].dt.hour.unique())
    else:
        # Инициализация списка
        hour_list = []
        # Добавление hour в hour_list
        if isinstance(hour, list):
            hour_list.extend(hour)
        else:
            hour_list.append(hour)

    # Фильтрация данных по указанным году, месяцу и часу
    filtered_df = df_data.loc[((df_data['year'].isin(year_list)) &
                               (df_data['month'].isin(month_list)) &
                               (df_data['hour'].isin(hour_list)))]

    # Построение treemap с добавлением рамки для px.Constant('all')
    fig = px.treemap(data_frame=filtered_df,
                     path=[px.Constant('all'), 'Ур. напряж. расч.', 'id_Объект'],
                     values='value',
                     title=f'Treemap for Year: {year}, Month: {month}, Hour: {hour}')

    # Настройка внешнего вида рамки
    fig.update_traces(marker=dict(line=dict(color="gray", width=2)))  # Настройка рамки
    fig.update_traces(root_color="lightgrey")

    # Возвращение фигуры для дальнейшего использования
    return fig

#Доля объемов по уровням напряжения
def print_create_pie_charts(df_data):
    # Убедитесь, что столбец 'year' является целым числом
    df_data['year'] = df_data['date'].dt.year

    # Определение последних трех лет
    last_three_years = sorted(df_data['year'].unique())[-3:]

    # Создание подграфиков
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=[f'Year: {year}' for year in last_three_years],
        specs=[[{'type': 'pie'}, {'type': 'pie'}, {'type': 'pie'}]]
    )

    # Создание диаграмм для каждого года
    for i, year in enumerate(last_three_years):
        year_df = df_data[df_data['year'] == year]
        pie_chart = go.Pie(
            labels=year_df['Ур. напряж. расч.'],
            values=year_df['value'],
            name=f'Year: {year}',
            textinfo='label+percent',  # Показать метки и проценты
            insidetextorientation='radial'  # Ориентация текста внутри диаграммы
        )

        fig.add_trace(pie_chart, row=1, col=i + 1)

    # Обновление макета фигуры
    fig.update_layout(
        title_text='Pie Charts for the Last Three Years',
        showlegend=True,
        height=400,
        width=1200,
        annotations=[dict(
            text=f'Year: {year}',
            x=0.5 + (i - 1) * 0.33,
            y=1.1,
            xref='paper',
            yref='paper',
            showarrow=False,
            font=dict(size=14)
        ) for i, year in enumerate(last_three_years)]
    )

    # Показать фигуру
    return fig

#Распределение доли по уровням напряжения по объектам
def print_create_boxplot(df_data):
    # Создание боксплота
    fig = px.box(
        data_frame=df_data,
        x='id_Объект',
        y='value',
        color='id_Объект'  # Цвет боксплотов в зависимости от 'id_Объект'
    )

    # Отображение графика
    return fig

def create_mapbox_scatter_point(geojson_file, zoom=13):
    # Загрузка данных из GeoJSON файла
    with open(geojson_file, 'r') as file:
        data = json.load(file)

    # Извлечение координат из файла GeoJSON (предполагается, что данные содержат 'Point' типы объектов)
    latitudes = []
    longitudes = []

    for feature in data['features']:
        # Проверяем, что тип геометрии - 'Point'
        if feature['geometry']['type'] == 'Point':
            longitude, latitude = feature['geometry']['coordinates']
            latitudes.append(latitude)
            longitudes.append(longitude)

    # Создание scattermapbox с заданными параметрами
    fig = go.Figure(go.Scattermapbox(
        lat=latitudes,  # Широты из файла
        lon=longitudes,  # Долготы из файла
        mode='markers',  # Режим отображения - маркеры
        marker=go.scattermapbox.Marker(size=10)  # Размер маркеров
    ))

    # Настройки карты
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",  # Стиль карты
            center=dict(lat=sum(latitudes) / len(latitudes), lon=sum(longitudes) / len(longitudes)),
            # Центр карты - среднее по координатам
            zoom=zoom  # Начальный уровень масштабирования
        ),
        showlegend=False,  # Отключение легенды
        margin={"r": 0, "t": 0, "l": 0, "b": 0},  # Убираем все отступы
        height=None,  # Высота на весь холст (None убирает фиксированную высоту)
        width=None  # Ширина на весь холст (None убирает фиксированную ширину)
    )

    # Возвращение фигуры
    return fig

def print_create_line_plot(df, column, id_value):
    id = id_value
    column = 'id_Объект'
    list_id = []
    # Добавление id в list_id

    if isinstance(id, list):  # Проверяем, является ли id списком
        list_id.extend(id)  # Если да, добавляем элементы этого списка в list_id
    else:
        list_id.append(id)  # Если нет, добавляем само значение id в list_id

    # Фильтруем DataFrame по 'id_ТУ' и выбираем колонку 'value'
    filtered_df = df[df[column].isin(list_id)]

    # Группируем по колонке 'date' и суммируем значения в колонке 'value'
    filtered_df = filtered_df.groupby('date')[['value']].sum().reset_index()

    # Рассчитываем среднее значение за сутки
    daily_mean = filtered_df.resample('D', on='date')['value'].mean().reset_index()

    # Создаем график с исходными данными
    fig = go.Figure()

    # Добавляем исходные данные на график
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['value'],
                             mode='lines', name='Значения',
                             line=dict(color='blue', width=1),
                             opacity=0.5))  # Устанавливаем прозрачность

    # Добавляем на график средние значения за сутки
    fig.add_trace(go.Scatter(x=daily_mean['date'], y=daily_mean['value'],
                             mode='lines', name='Среднее за сутки',
                             line=dict(color='red', width=2)))

    # Настройки графика
    fig.update_layout(
        title=f'Значения и средние значения за сутки для {id}',
        xaxis_title='Дата',
        yaxis_title='кВт',
        legend=dict(
            x=1,  # Позиция по оси X (1 - крайняя правая позиция)
            y=1,  # Позиция по оси Y (1 - верхняя позиция)
            traceorder='normal',
            font=dict(
                size=12,
            ),
            # bgcolor='LightSteelBlue',
            # bordercolor='Black',
            # borderwidth=1,
            xanchor='left',
            yanchor='top'
        )
    )

    return fig


def create_consumption_bar_chart(df_data, df_pnr, id_object):
    list_id_object = []

    if isinstance(id_object, list):
        list_id_object.extend(id_object)
    else:
        list_id_object.append(id_object)

    # Объединяем df_data и df_pnr по столбцу 'дата-время', чтобы получить только те строки, которые совпадают с часами пиковой нагрузки
    df_merged = pd.merge(df_data, df_pnr[['RegionPeakDateHour_hour']], left_on='date',
                         right_on='RegionPeakDateHour_hour', how='inner')

    # Добавляем столбцы для года и месяца, чтобы группировать данные по месяцам
    df_merged['год'] = df_merged['RegionPeakDateHour_hour'].dt.year
    df_merged['месяц'] = df_merged['RegionPeakDateHour_hour'].dt.month

    # Сначала суммируем значения по объектам для каждой даты
    df_summed = df_merged.groupby(['id_Объект', 'RegionPeakDateHour_hour'])['value'].sum().reset_index()

    df_summed['год'] = df_summed['RegionPeakDateHour_hour'].dt.year
    df_summed['месяц'] = df_summed['RegionPeakDateHour_hour'].dt.month

    # Затем вычисляем среднее значение этих сумм по месяцам для указанного объекта
    result = df_summed[df_summed['id_Объект'].isin(list_id_object)].groupby(['id_Объект', 'год', 'месяц'])[
        'value'].mean().reset_index()

    # Переименовываем столбец 'value' в 'среднее потребление'
    result.rename(columns={'value': 'среднее потребление'}, inplace=True)

    # Объединяем год и месяц в один столбец для оси X
    result['год_месяц'] = result['год'].astype(str) + '-' + result['месяц'].astype(str)

    # Строим bar-chart
    fig = px.bar(result,
                 x='год_месяц',
                 y='среднее потребление',
                 color='id_Объект',
                 barmode='group',
                 labels={'год_месяц': 'Year-Month', 'среднее потребление': 'Average Consumption'},
                 title=f'Average Consumption per Month for Object {id_object}')

    return fig


def create_histogram_with_boxplot(df_data, column='Ур. напряж. расч.', volt_list=['ВН', 'СН1', 'СН2'], nbins=73):
    """
    Функция для создания гистограммы с боксовым графиком сверху на основе фильтрации по значению столбца.

    :param df_data: DataFrame с исходными данными.
    :param column: Столбец для фильтрации (например, 'Ур. напряж. расч.').
    :param volt_list: Список значений для фильтрации в столбце (например, ['ВН', 'СН1', 'СН2']).
    :param nbins: Количество карманов (по умолчанию 73).
    :return: Объект fig с построенным графиком.
    """

    # Фильтрация данных по значениям в столбце
    filtered_data = df_data[df_data[column].isin(volt_list)]

    # Группировка по дате и столбцу, затем расчет среднего значения для 'value'
    grouped_data = filtered_data.groupby([filtered_data['date'], column])['value'].sum().reset_index()

    # Построение гистограммы с боксовым графиком сверху и карманами
    fig = px.histogram(
        data_frame=grouped_data,
        #x='value',
        x='value',
        color=column,
        hover_data=grouped_data.columns,
        marginal='box',  # Боксовый график сверху
        nbins=nbins  # Установка количества карманов
    )

    return fig

def print_network_power(monthly_average, type_layout: str):
    # Построение графика в зависимости от выбранного типа разметки
    if type_layout == 'Ур. напряж. расч.':
        fig = px.bar(monthly_average,
                     x='год_месяц',
                     y='сетевая мощность',
                     color='Ур. напряж. расч.',
                     barmode='group',
                     labels={'год_месяц': 'Year-Month', 'сетевая мощность': 'Average Consumption'},
                     title='Average Consumption per Object per Month')
    elif type_layout == 'id_Объект':
        fig = px.bar(monthly_average,
                     x='год_месяц',
                     y='сетевая мощность',
                     color='id_Объект',
                     barmode='group',
                     labels={'год_месяц': 'Year-Month', 'сетевая мощность': 'Average Consumption'},
                     title='Average Consumption per Object per Month')

    return fig

def calculate_network_power(df_data, df_ppn, df_pnr):
    # Преобразуем столбец с датой в формат даты (без времени)
    f_data = df_data.copy(deep=True)
    f_data['дата'] = f_data['date'].dt.date
    df_pnr['дата'] = df_pnr['RegionPeakDateHour_hour'].dt.date

    # Фильтрация данных по рабочим дням, которые содержатся в производственном календаре
    f_data = f_data[f_data['дата'].isin(df_pnr['дата'])]

    # Объединяем данные потребления с данными о плановой пиковой нагрузке по началу периода нагрузки
    f_data = f_data.merge(df_ppn[['начало_дата_час', 'конец_дата_час']], how='inner', left_on='date', right_on='начало_дата_час')

    # Оставляем только те строки, которые находятся в пределах интервала плановой пиковой нагрузки
    f_data = f_data[(f_data['date'] >= f_data['начало_дата_час']) & (f_data['date'] <= f_data['конец_дата_час'])]

    # Извлекаем год и месяц из даты для последующей группировки
    f_data['year'] = f_data['date'].dt.year
    f_data['month'] = f_data['date'].dt.month

    # Нахождение максимального значения потребления для каждого объекта и уровня напряжения за каждый рабочий день
    daily_max = f_data.groupby(['id_Объект', 'дата', 'year', 'month', 'Ур. напряж. расч.'])['value'].max().reset_index()

    # Вычисляем среднее значение максимальных нагрузок по месяцам для каждого объекта и уровня напряжения
    monthly_average = daily_max.groupby(['id_Объект', 'year', 'month', 'Ур. напряж. расч.'])['value'].mean().reset_index()

    # Переименовываем столбец 'value' в 'сетевая мощность'
    monthly_average.rename(columns={'value': 'сетевая мощность'}, inplace=True)

    # Добавляем столбец с объединением года и месяца для удобства отображения
    monthly_average['год_месяц'] = monthly_average['year'].astype(str) + '-' + monthly_average['month'].astype(str)

    return monthly_average
