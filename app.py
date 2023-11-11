# 1. Import Library & read data source
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash_auth                          #lib u/ passwrd

### Import data disini

paxel_palette = ['#ffc107', '#fd7e14', '#dc3545', '#e83e8c', '#6f42c1']
import json
with open('data_cache/Indonesia_provinces.geojson', 'r') as geojson_file:
    geojson_data = json.load(geojson_file)

shipping = pd.read_pickle('data_input/shipping_clean') #membaca data source, bisa di rubah ke lsg konek ke databse (BQ/posgrest),
                                                       #setiap perubahn di tabel akan automatis merubah didashboard

#import username & pass
VALID_USERNAME_PASSWORD_PAIRS = {
    'biadmin': 'paxel321'
}
#------------------------------------------------------------------------
### Info card disini

# Menghitung Total Pesanan
total_pesanan = shipping['order_id'].count()

# Menghitung Completed rate
completed_rate = (shipping[shipping['status'] == 'Completed']['order_id'].count() / total_pesanan)*100

# Menghitung Rata-rata Waktu Pengiriman
delivery_time = shipping['day_to_arv'].mean()

# Mendefisiniskan card content (nilai/value) dr card trsebut
card_total_pengiriman = [
    dbc.CardHeader("Total Pengiriman",style={'text-align':'left',
                                                        'color':"white"
                                                        }),
    dbc.CardBody(
        [
            html.H1(f"{total_pesanan:,}", className="card-title",style={'color': 'white',
                                                      }),
            
        ]
    ),
]

card_completed_rate = [
    dbc.CardHeader("Persentase Pengiriman Selesai",style={'text-align':'left',
                                                        'color':"white"
                                                        }
                   ),
    dbc.CardBody(
        [
            html.H1(f"{completed_rate:.2f}%", className="card-title",
                                            style={'color': 'white',
                                                      }),
            
        ]
    ),
]

card_delivery_time = [
    dbc.CardHeader("Rata-Rata Waktu Pengiriman",style={'text-align':'left',
                                                        'color':"white"
                                                        }
                   ),
    dbc.CardBody(
        [
            html.H1(f"{delivery_time:.0f} hari", className="card-title",
                                                style={'color': 'white',
                                                      }),
            
        ]
    ),
]

card_dropdown = [
    dbc.CardHeader("Pilih Mode Pengiriman",style={'text-align':'left',
                                                        'color':"white"
                                                        }
                   ),
    dbc.CardBody(
        [
            dcc.Dropdown(
                options= shipping['ship_mode'].unique(),
                value= 'FIRST CLASS', #VALUE awal yg di munculkan
                id= 'List_ship_mode', #bebas menamai (nilai sbg identitas aja)
            )
            
        ]
    ),
]


##--Menampilkan chloropleth map--
province_data = shipping.pivot_table(
    index='province',
    values='order_id',
    aggfunc='count'
).reset_index()

fig_map = px.choropleth(province_data,    ## assign ke nama var fig_map agar mudah u/di panggil kedepan nya
                   geojson=geojson_data,
                   locations='province',
                   color='order_id',
                   color_continuous_scale=paxel_palette,
                   featureidkey='properties.NAME_1',
                   title='Peta Pengiriman Paket Ke Seluruh Provinsi di Indonesia',
                   hover_name='province',
                   template='plotly_white',
                   projection='equirectangular',
                   labels={'order_id': 'Jumlah Pesanan',
                           'province': 'Provinsi'}
                   )

fig_map = fig_map.update_geos(fitbounds='locations', visible=False)

# ------------------------DONUT CHART--------------------------------------
# data aggregation
ship_mode = shipping.pivot_table(
    index = 'ship_mode',
    values = 'order_id',
    aggfunc = 'count'
).reset_index()

# data visualization
fig_donut = px.pie(
    ship_mode,
    values = 'order_id',
    names = 'ship_mode',
    hole = 0.4, # untuk membuat hole pada pie chart
    color_discrete_sequence = ['#ffc107', '#e83e8c', '#6f42c1'],
    title = 'Jumlah Pengiriman Disetiap Status Pengiriman',
    labels = {
        'ship_mode': 'Mode Pengiriman',
        'order_id': 'Jumlah Pengiriman'
    },
    template = 'plotly_white',
)


#---------------------------------------------------------------------------------------
# 2. Create Dashboard Instance

app = Dash(
    external_stylesheets=[dbc.themes.PULSE],
    name='Dashboard - Pengiriman COD'
    ) #pilih tema yg sdh di sediakan DASH

server=app.server

##----menambhakan usrname & pass-----------
auth = dash_auth.BasicAuth(                 #memanggil usrnme & pass
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
#---------------------------------------------------------------------------------------
app.title = 'Dashboard - Pengiriman COD'

navbar = dbc.NavbarSimple(             #pilih/definiskan layout navigasi page/halaman web
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
        
    ],
    brand="Dashboard Pengiriman COD",
    brand_href="#",
    color="#5e50a1",
    dark=True,
)

#---------------------------USER INTERFACE---------------------------------------------
## Kode untuk menampilkan apapun di halaman website kita
app.layout = html.Div(children=[
    navbar,
    html.Br(), ## u/ nambah spasi antar baris

    html.Div(
     [
    ##-----ROW 1-------
      dbc.Row(
        [
        ##----COL 1---
        dbc.Col(
            [
                dbc.Card(
                    card_total_pengiriman,
                    color='#5e50a1'
                ),
                 html.Br(), ## u/space paragraph
                 dbc.Card(
                    card_completed_rate,
                    color='#414042'
                ),
                 html.Br(), ## u/space paragraph
                 dbc.Card(
                   card_delivery_time,
                    color='#ffb200'
                ),
            ],
            width=3 #atur lebar card skala 1-12(standard total 12 u/ 1 hal web)
        ),
        ##--- COL 2---
        dbc.Col(
            [
                dcc.Graph(figure=fig_map) #panggil var fig_map yg mw di tampilkan
            ]  #(optional ditullis/tidak gpp)tambah parameter width=9 u/ atur lebar card skala 1-12(standard total 12 u/ 1 hal web)
        ),
        ]
      ),
      html.Br(),

      html.Hr(), #penambahan garis horizontal di html

      html.Br(),

      #----------------------Row 2------------------------------------------------------------
      dbc.Row(
          [
              html.H1("Analisis Mode Pengiriman",style={'text-align':'center',
                                                        'color':"#5e50a1",
                                                        'font-size':'24px'
                                                        }),
              html.Br(), html.Br(),

              #Row 2 Col 1-----------------------
              dbc.Col(
                  [
                      dbc.Card(card_dropdown, color='#5e50a1'),
                         html.Br(),
                         dcc.Graph(
                                figure=fig_donut, #panggil var fig_donut gambar chart donut yg sdh di definisikan terlbh dhlu di atas
                                style= {
                            'width': '400px',
                            'height': '400px'},
                            ) 
                  ],
                  width=3 #atur lebar card skala 1-12(standard total 12 u/ 1 hal web)
              ),
              #Row 2 Col 2------------------------
              dbc.Col(
                  [
                      dbc.Tabs(
                          [
                              ##tab 1: Pergerakan Harian
                              dbc.Tab(dcc.Graph(id = 'lineplot'), label='Pergerakan Harian'),

                              ##Tab 2: Jumlah Pengiriman Harian
                              dbc.Tab(dcc.Graph(id = 'heatmap'), label='Jumlah Pengiriman Harian'),

                              ##Tab 3: Dissable (dalam kondisi tidak aktif/tdk di munculkan)
                              dbc.Tab(label='Total Revenue', disabled=True),
                          ]
                      ),
                  ]
              ),
          ]
      ),
     ]
    ),


],
style={
    'background-color':'white'
}
)


##-----------CALLBACK INPUT & OUTPUT-----------------------------
@app.callback(
    [
        Output('lineplot', 'figure'),
        Output('heatmap', 'figure'),
        Input('List_ship_mode', 'value'),
    ]
)

def update_plots(shipping_mode):

    standard = shipping[shipping['ship_mode'] == shipping_mode]

    # Data aggregation
    line_agg = standard.pivot_table(
        index='creation_date',
        values='order_id',
        aggfunc='count'
    ).reset_index()


    # data visualization
    fig_line = px.line(
        line_agg,
        x = 'creation_date',
        y = 'order_id',
        color_discrete_sequence = ['#6f42c1'],
        title = 'Pergerakan Pengiriman Paket Harian',
        template = 'plotly_white',
        labels = {
            'order_id': 'Jumlah Pengiriman',
            'creation_date': ''
        }
        
    )

    data_agg1 = standard.pivot_table(
        values='day_to_arv',
        index='order_day',
        columns='order_hour',
        aggfunc='count',
        ).reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    #data_agg1

    # data visualization
    fig_heatmap = px.imshow(
        data_agg1,
        color_continuous_scale = paxel_palette,
        template = 'plotly_white',
        )
    fig_heatmap = fig_heatmap.update_xaxes(title_text='Waktu Pesanan', dtick=1)
    fig_heatmap = fig_heatmap.update_yaxes(title_text='Hari Pesanan')


    return fig_line, fig_heatmap

#------------------------------------------------------------------------
# 3. Start the Dash Server

if __name__ == '__main__':
    app.run(debug=True)
