
import pandas as pd
import dash_bootstrap_components as dbc
import dash
import dash_core_components as dcc
import dash_html_components as html

# Hacer un dataframe con data de firebase


def dataFrameFromData(data):
    df = pd.DataFrame(
        {'Valor': list(data.values())},
        index=data.keys()
    )
    return df

# Poner un salto de linea en los ejes de plotly


def br(list1):
    l2 = []
    for ele in list1:
        l2.append(ele.replace(" ", "<br>"))
    return l2


# Añadir comas de miles
def addComa(num):
    if isinstance(num, str) == False:
        num = str(num)
    #"Adicionar comas como separadores de miles a n. n debe ser de tipo string"
    s = num
    if "-" in s:
        s = s.replace("-", "")
        try:
            i = s.index('.')  # Se busca la posición del punto decimal
        except ValueError:
            i = len(s)
        while i > 3:
            i = i - 3
            s = s[:i] + ',' + s[i:]
        s = "-{}".format(s)
    else:
        try:
            i = s.index('.')  # Se busca la posición del punto decimal
        except ValueError:
            i = len(s)
        while i > 3:
            i = i - 3
            s = s[:i] + ',' + s[i:]
    return s

# Puntos x comas


def dotxcom(string):

    if isinstance(string, str) == False:

        string = str(string)

    string = string.replace(",", "*")

    string = string.replace(".", ",")

    string = string.replace("*", ".")

    return string


# Formato numerico colombia
def colFormat(num):
    x = addComa(num)
    x = dotxcom(x)
    return x


dict_nombre_indicadores = {
    1: 'Población',
    2: 'Bienestar Social',
    3: 'Producción',
    4: 'Empleo'
}


# Crear acordeon loop
def make_item(i, data):

    if data != None:
        # we use this function to make the example items to avoid code duplication
        return dbc.Card(
            [
                dbc.CardHeader(
                    html.H2(
                        dbc.Button(
                            dict_nombre_indicadores[i],
                            color="link",
                            id=f"group-{i}-toggle",
                        )
                    )
                ),
                dbc.Collapse(
                    dbc.CardBody([
                        html.Div(
                            [html.Strong(key), html.Span(
                                data[key], className="list-data-span")],
                            className="list-data")
                        for key in list(data.keys())]),
                    id=f"collapse-{i}",
                ),
            ]
        )
    else:
        return dbc.Card(
            [
                dbc.CardHeader(
                    html.H2(
                        dbc.Button(
                            dict_nombre_indicadores[i],
                            color="link",
                            id=f"group-{i}-toggle",
                        )
                    )
                ),
                dbc.Collapse(
                    dbc.CardBody([
                        html.Span("No hay datos disponibles")]),
                    id=f"collapse-{i}",
                ),
            ]
        )
