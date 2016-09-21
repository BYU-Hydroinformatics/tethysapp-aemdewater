import sys
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import numpy as np
import math

from tethys_sdk.gizmos import *


@login_required()

def home(request):
    """
    Controller for the construction dewatering simulator
    """
    # Define view options
    view_options = MVView(
        projection='EPSG:4326',
        center=[-111.64925, 40.24721],
        zoom=16.5,
        maxZoom=22,
        minZoom=2
    )

    # Define drawing options
    drawing_options = MVDraw(
        controls=['Delete', 'Move', 'Point', 'Box', 'Polygon'],
        initial='Box',
        output_format='WKT'
    )

    # Define map view options
    map_view_options = MapView(
            height='600px',
            width='100%',
            controls=['ZoomSlider', 'Rotate', 'FullScreen',
                      {'MousePosition': {'projection': 'EPSG:4326'}},
                      {'ZoomToExtent': {'projection': 'EPSG:4326', 'extent': [-130, 22, -65, 54]}}],
            layers=[],
            view=view_options,
            basemap='OpenStreetMap',
            draw=drawing_options,
            legend=True
    )

    # Define text input boxes for UI
    k = TextInput(display_text='Average Hydraulic Conductivity',
                  name='k',
                  initial='0.000231',
                  placeholder='e.g. 0.000231',
                  prepend='k =',
                  append='[ft/s]',
                  )
    bedrock = TextInput(display_text='Bedrock Elevation',
                  name='bedrock',
                  initial='0',
                  placeholder='e.g. 0',
                  prepend='Elev. =',
                  append='[ft]',
                  )
    iwte = TextInput(display_text='Initial Water Table Elevation',
                  name='iwte',
                  initial='100',
                  placeholder='e.g. 100',
                  prepend='Elev. =',
                  append='[ft]',
                  )
    q = TextInput(display_text='Total Combined Flow',
                  name='q',
                  initial='2',
                  placeholder='e.g. 2',
                  prepend='Q =',
                  append='[cfs]',
                  )
    dwte = TextInput(display_text='Desired Water Table Elevation',
                  name='dwte',
                  initial='70',
                  placeholder='e.g. 70',
                  prepend='Elev. =',
                  append='[ft]',
                  )

    execute = Button(display_text='Calculate Water Table Elevations',
                     attributes='onclick=app.dewater();',
                     submit=True,
                     classes='btn-success')

    instructions = Button(display_text='Instructions',
                     attributes='onclick=generate_water_table',
                     submit=True)

    context = { 'page_id' : '1', 'map_view_options': map_view_options,
                'k':k,
                'bedrock':bedrock,
                'iwte':iwte,
                'q':q,
                'dwte':dwte,
                'execute':execute,
                'instructions':instructions}

    return render(request, 'aemdewater/home.html', context)


def generate_water_table(request):

    #set module paths for timml repository
    sys.path.append("/home/jacobbf1/tethysdev/tethysapp-aemdewater/tethysapp/aemdewater/aem")
    sys.path.append("/usr/local/lib/python2.7/dist-packages")
    sys.path.append("/usr/lib/python2.7/dist-packages")

    # print os.getcwd()
    # print sys.path

    from timml import *
    # import matplotlib.pyplot
    # matplotlib.use('PS')
    # import matplotlib.pyplot
    # matplotlib.pyplot.ioff()
    # matplotlib.pyplot.close("all")

    import Tkinter as tk
    root = tk.Tk()


    get_data = request.GET

    xIndex = json.loads(get_data['xIndex'])
    yIndex = json.loads(get_data['yIndex'])
    wXCoords = json.loads(get_data['wXCoords'])
    wYCoords = json.loads(get_data['wYCoords'])
    cellSide = json.loads(get_data['cellSide'])
    initial = float(json.loads(get_data['initial']))
    bedrock = float(json.loads(get_data['bedrock']))
    q = float(json.loads(get_data['q']))
    k = float(json.loads(get_data['k']))

    waterTable = []

    #This is the analytic element model test, retrieving heads for now
    ml = Model(k = [k], zb = [bedrock], zt = [initial])
    Constant(ml,wXCoords[0]+500,wYCoords[0]+500,initial,[0])

    # print (xIndex[0]+500)
    # print (yIndex[0]+500)

    # Add the wells to the analytic element model

    pumpRate = (q / len(wYCoords))
    print pumpRate

    i = 0
    while (i < len(wYCoords)):
        Well(ml,wXCoords[i],wYCoords[i],pumpRate,10,0)
        # print wXCoords[i]
        # print wYCoords[i]
        i = i + 1
        # print len(wYCoords)

    #
    ml.solve(doIterations=True)

    # contourList = timcontour(ml, 0, 20000, 50, 0, 20000, 50, 3, 20, newfig = True, returncontours = True)
    # matplotlib.pyplot.clf()
    # matplotlib.pyplot.cla()
    # matplotlib.pyplot.close("all")

    root.destroy()

    print "TimML generated heads"

    print ml.head(0,wXCoords[0]-cellSide,wYCoords[0]+cellSide)
    print ml.head(0,wXCoords[0],wYCoords[0]+cellSide)
    print ml.head(0,wXCoords[0]+cellSide,wYCoords[0]+cellSide)
    print ml.head(0,wXCoords[0]-cellSide,wYCoords[0])
    print ml.head(0,wXCoords[0],wYCoords[0])
    print ml.head(0,wXCoords[0]+cellSide,wYCoords[0])
    print ml.head(0,wXCoords[0]-cellSide,wYCoords[0]-cellSide)
    print ml.head(0,wXCoords[0],wYCoords[0]-cellSide)
    print ml.head(0,wXCoords[0]+cellSide,wYCoords[0]-cellSide)

    print " "

    print "EQN generated heads"

    print elevationCalc(wXCoords[0]-cellSide,wYCoords[0]+cellSide,wXCoords,wYCoords,cellSide,initial,bedrock,q,k)
    print elevationCalc(wXCoords[0],wYCoords[0]+cellSide,wXCoords,wYCoords,cellSide,initial,bedrock,q,k)
    print elevationCalc(wXCoords[0]+cellSide,wYCoords[0]+cellSide,wXCoords,wYCoords,cellSide,initial,bedrock,q,k)
    print elevationCalc(wXCoords[0]-cellSide,wYCoords[0],wXCoords,wYCoords,cellSide,initial,bedrock,q,k)
    print elevationCalc(wXCoords[0],wYCoords[0],wXCoords,wYCoords,cellSide,initial,bedrock,q,k)
    print elevationCalc(wXCoords[0]+cellSide,wYCoords[0],wXCoords,wYCoords,cellSide,initial,bedrock,q,k)
    print elevationCalc(wXCoords[0]-cellSide,wYCoords[0]-cellSide,wXCoords,wYCoords,cellSide,initial,bedrock,q,k)
    print elevationCalc(wXCoords[0],wYCoords[0]-cellSide,wXCoords,wYCoords,cellSide,initial,bedrock,q,k)
    print elevationCalc(wXCoords[0]+cellSide,wYCoords[0]-cellSide,wXCoords,wYCoords,cellSide,initial,bedrock,q,k)

    # try:
    #     count = 0
    #     while (count<100):
    #         print contourList.collections[count].get_paths()
    #         print count
    #         count = count + 1
    # except:
    #     pass

    # This section constructs the featurecollection polygons defining the water table elevations
    # Cells are defined at the corners, water table elevation is defined at the center of the cell

    for long in np.arange(xIndex[0]-cellSide, xIndex[1]+cellSide, cellSide):
        for lat in np.arange(yIndex[0]-cellSide, yIndex[1]+cellSide, cellSide):
            waterTable.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                                    [   [long,lat],
                                        [long + cellSide, lat],
                                        [long + cellSide, lat + cellSide],
                                        [long, lat + cellSide],
                                        [long,lat]
                                    ]
                                   ]
                    },
                    'properties': {
                        # 'elevation' : elevationCalc(long,lat,wXCoords,wYCoords,cellSide,initial,bedrock,q,k),
                        'elevation' : ml.head(0,(long+cellSide/2),(lat+cellSide/2)),
                    }
            })
            # if (wXCoords[0]-cellSide < long < wXCoords[0]+cellSide):
            #     if (wYCoords[0]-cellSide < lat < wYCoords[0]+cellSide):
            #         print elevationCalc(long,lat,wXCoords,wYCoords,cellSide,initial,bedrock,q,k)

    return JsonResponse({
        "sucess": "Data analysis complete!",
        "local_Water_Table": json.dumps(waterTable)
    })


# Assign elevations to raster grid
def elevationCalc (long, lat, wXCoords,wYCoords,cellSide, initial, bedrock, q, k):
    H = initial - bedrock

    i = 0
    sum = 0.0
    minr = 0.05

    while (i < len(wXCoords)):

        wellx = wXCoords[i]
        welly = wYCoords[i]
        Q = q/len(wXCoords)

        deltax = abs(long+cellSide/2-wellx)
        deltay = abs(lat+cellSide/2-welly)

        wellr = pow((pow(deltax,2) + pow(deltay,2)),0.5)

        #Make sure that we don't create a complex value for the water table elevation
        #(Previous Trial) math.exp(math.log(500)-math.pi*k*pow(H,2)/Q)
        if (wellr < minr):
            wellr = minr
            sum = sum + Q*math.log(500/wellr)

        elif (math.log(500/wellr)<0):
            sum = sum

        else:
            sum = sum + Q*math.log(500/wellr)
        i = i+1

    wtElevation = math.pow(abs(math.pow(H,2) - sum/(math.pi*k)),0.5) + bedrock
    # print wtElevation # for debugging purposes
    return (round(wtElevation, 2))



