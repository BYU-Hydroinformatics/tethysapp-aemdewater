import sys
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import numpy as np


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
        controls=['Delete', 'Move', 'Point', 'Box'],     # , 'Polygon', 'LineString'
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
                  append='[ft^3/s]',
                  )
    dwte = TextInput(display_text='Desired Water Table Elevation',
                  name='dwte',
                  initial='70',
                  placeholder='e.g. 70',
                  prepend='Elev. =',
                  append='[ft]',
                  )

    # Define Toggle switch for slurry trench being enabled

    slurry = ToggleSwitch(display_text='Enable Slurry Trench Boundary',
                          name='slurry',
                          attributes='')

    slurryK = TextInput(display_text='Slurry Hydraulic Conductivity',
                        name='slurryK',
                        initial='0.00000000347',
                        placeholder='e.g. 3.47E-9',
                        prepend='k =',
                        append='[ft/s]',
                        )
    slurryT = TextInput(display_text='Slurry Wall Thickness',
                    name='slurryT',
                    initial='3',
                    placeholder='e.g. 3',
                    prepend='t =',
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
                'instructions':instructions,
                'slurry':slurry,
                'slurryK':slurryK,
                'slurryT':slurryT}

    return render(request, 'aemdewater/home.html', context)


def generate_water_table(request):

    #set module paths for timml repository
    sys.path.append("/var/www/tethys/apps/tethysapp-aemdewater/tethysapp/aemdewater/timml")
    sys.path.append("/usr/local/lib/python2.7/dist-packages")
    sys.path.append("/usr/lib/python2.7/dist-packages")

    # print os.getcwd()
    # print sys.path
    try:
        from timml import *
    except Exception,e:
        print str(e)
        return JsonResponse({"error":str(e)})
    import matplotlib.pyplot
    # matplotlib.use('PS')

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

    # slurry trench information
    slurry = json.loads(get_data['slurry'])
    slurryK = float(json.loads(get_data['slurryK']))
    slurryT = float(json.loads(get_data['slurryT']))
    pXCoords = json.loads(get_data['pXCoords'])
    pYCoords = json.loads(get_data['pYCoords'])
    xylist1 = []
    xylist2 = []

    #This is the analytic element model test, retrieving heads for now
    ml = Model(k = [k], zb = [bedrock], zt = [initial])

    if(slurry):
        print "Starting slurry simulation"
        # Define Exterior Boundary of Slurry Trench
        xylist1.append([pXCoords[0]-slurryT/2,pYCoords[0]-slurryT/2])
        xylist1.append([pXCoords[1]-slurryT/2,pYCoords[1]+slurryT/2])
        xylist1.append([pXCoords[2]+slurryT/2,pYCoords[2]+slurryT/2])
        xylist1.append([pXCoords[3]+slurryT/2,pYCoords[3]-slurryT/2])
        print xylist1

        #Define Interior Boundary of Slurry Trench
        xylist2.append([pXCoords[0]+slurryT/2,pYCoords[0]+slurryT/2])
        xylist2.append([pXCoords[1]+slurryT/2,pYCoords[1]-slurryT/2])
        xylist2.append([pXCoords[2]-slurryT/2,pYCoords[2]-slurryT/2])
        xylist2.append([pXCoords[3]-slurryT/2,pYCoords[3]+slurryT/2])
        print xylist2

        PolygonInhom(ml,k=[k],c=[],zb=[bedrock],zt=[initial],xylist=xylist2)
        PolygonInhom(ml,k=[slurryK],c=[],zb=[bedrock],zt=[initial],xylist=xylist1)

        MakeInhomPolySide(ml, xylist=xylist2, order=5, closed=True)
        MakeInhomPolySide(ml, xylist=xylist1, order=5, closed=True)


    Constant(ml,wXCoords[0]+500,wYCoords[0]+500,initial,[0])

    # Add the wells to the analytic element model

    pumpRate = (q / len(wYCoords))
    print pumpRate

    i = 0
    while (i < len(wYCoords)):
        Well(ml,wXCoords[i],wYCoords[i],pumpRate,0.5,0)
        i = i + 1
        # print len(wYCoords)

    #
    ml.solve(doIterations=True)



    contourList = timcontour(ml, xIndex[0], xIndex[1], np.absolute((xIndex[0]-xIndex[1])/cellSide), yIndex[0],
                             yIndex[1], np.absolute((yIndex[0]-yIndex[1])/cellSide), levels = 10,
                             newfig = True, returncontours = True)
    root.destroy()
    # matplotlib.pyplot.close("all")

    # Return the contour paths and store them as a list
    contourPaths = []

    # This retrieves the heads of each contour traced by TimML and stores them in intervals[]
    intervals = []
    i = 0

    retrieveIntervals = contourList.levels
    try:
        while(i<10):
            intervals.append(retrieveIntervals[i])
            i += 1
    except:
        pass

    # print intervals

    # Retrieves the contour traces and stores them in contourPaths[]
    i = 0
    try:
        while (i < 10):
            print i
            contourPaths.append(contourList.collections[i].get_paths())
            i += 1
    except:
        pass

    # print contourPaths


    # This section constructs the featurecollection polygons defining the water table elevations
    # Cells are defined at the corners, water table elevation is defined at the center of the cell

    waterTable = []

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
                        'elevation' : ml.head(0,(long+cellSide/2),(lat+cellSide/2)),
                    }
            })

    # This collects the contour lines and creates JSON objects for the response to AJAX request (to be drawn in js)

    Contours = []
    i = 0

    for path in contourList.collections:
        for segment in path.get_segments():
            trace = []
            for piece in segment:
                trace.append(piece.tolist())

            Contours.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': trace
                },
                'properties':{
                    'elevation' : intervals[i],
                }
            })
        i += 1

    # print "Showing the Contour Objects"
    # print Contours

    return JsonResponse({
        "sucess": "Data analysis complete!",
        "local_Water_Table": json.dumps(waterTable),
        "contours": json.dumps(Contours),
        "heads": json.dumps(intervals)
    })





