//  ################################# Global declarations ##################################################
"use strict";

function welcome_modal() {
    var myHTMLBody =
        "<p>This tool is used to aid in the design of a simple construction dewatering system in " +
        "an unconfined aquifer underlain by bedrock or a low permeability layer. The system consists " +
        "of one or more wells that fully penetrate the aquifer. Steps:</p>" +
            "<h6>1. Enter aquifer properties</h6>" +
                "<p>Enter the average hydraulic conductivity of the aquifer, the average bedrock elevation, " +
                "and the average water table elevation prior to pumping.</p>" +
                "<h6>2. Enter the project parameters</h6>" +
                "<p>Enter the total pumping rate (each well will pump an equal fraction of this amount and " +
                "the desired water table elevation (typically at or below the bottom of the planned excavation).</p>" +
            "<h6>3. Set map features</h6>" +
                "<p>Use the navigation tools on the map to locate your project and then use the rectangle tool to " +
                "indicate the location of your excavation and use the point tool on the map to enter the locations of " +
                "your wells.</p>" +
                "<h6>4. Perform calculations</h6>" +
                "<p>Click on the 'Calculate Water Table Elevations' tool to perform the drawdown calculations and " +
                "display the results on the map.</p>"+
				"<div align='center' id='Equation'><img src='/static/aemdewater/images/EQN.png'/></div>" +
				'</div>';
    modal_dialog("Instructions", myHTMLBody, true);
}

$(document).ready(function(){
    welcome_modal();
});

//  #################################### Verify that the user has the necessary variables ##############################

function verify(numFeatures, numWells, numPolys){
    //initialize the variables for the functions to be used

    if (isNaN(k.value)){
    	error_message('Hydraulic Conductivity must be a numeric value');
    	return false;
	}

	if (isNaN(bedrock.value)){
    	error_message('Bedrock Elevation must be a numeric value');
    	return false;
	}

	if (isNaN(iwte.value)){
    	error_message('Initial Water Table Elevation must be a numeric value');
    	return false;
	}

	if (isNaN(q.value)){
    	error_message('Total Combined Flow must be a numeric value');
    	return false;
	}

	if (isNaN(dwte.value)){
    	error_message('Desired Water Table Elevation must be a numeric value');
    	return false;
	}

    if (Number(dwte.value) < Number(bedrock.value)){
         error_message('Your desired elevation is lower than the bedrock elevation');
         return false;
    }

    if (Number(iwte.value) < Number(bedrock.value)){
        error_message('Your initial elevation is lower than the bedrock elevation');
        return false;
    }

    if (Number(dwte.value) > Number(iwte.value)){
        error_message('Your desired elevation is higher than the initial elevation');
        return false;
    }

    if (Number(k.value) <= 0){
        error_message('Hydraulic conductivity must have a positive value, adjust your input');
        return false;
    }

    if (Number(numFeatures)  == 0) {
        error_message("You don't have any features, please provide a boundary and well locations");
        return false;
    }

    if (Number(numWells) == 0) {
        error_message('You need wells to perform the analysis, please add at least one well');
        return false;
    }
    else if (Number(numPolys) == 0) {
        error_message('You need a boundary for your analysis, please add a boundary');
        return false;
    }
    else if (Number(numPolys) > 1) {
        error_message('You have more than one Perimeter, delete the extra(s)');
        return false;
    }

    //If you are to here without a return, everyting must be OK
    return true;
 };

function isOdd(num) {return !!(num % 2);}

//  #################################### From the input shapes and variables, create a grid ############################

function dewater(){

    var pCoords;
    var wCoords;
    var pXCoords = [];
    var pYCoords = [];
    var wXCoords = [];
    var wYCoords = [];
    var mapXCoords = [];
    var mapYCoords = [];
    var mapView;

    var map;
    var mapFeatures;
    var wells = [];
    var perimeter = [];
    var mapFeatures = [];

     //counters for building arrays
    var i = 0;
    var iX = 0;
    var iY = 0;

   //This method returns the OpenLayers map object.
    map = TETHYS_MAP_VIEW.getMap();

	toggle_legend(false,1);
	toggle_legend(false,2);

 //this reads the number of features found in the map object and verifies that all of the required features are present
    mapFeatures = map.getLayers().item(1).getSource().getFeatures();

    for (i = 0; i < mapFeatures.length; i++)  {
        if (map.getLayers().item(1).getSource().getFeatures()[i].getGeometry().getType() === 'Point') {
            wells.push(map.getLayers().item(1).getSource().getFeatures()[i].getGeometry().getCoordinates());
        }
        else if (map.getLayers().item(1).getSource().getFeatures()[i].getGeometry().getType() === 'Polygon') {
            perimeter.push(map.getLayers().item(1).getSource().getFeatures()[i].getGeometry().getCoordinates());
        }
    }

    //Check the inputs. Exit if there is a problem.
    if (!verify(mapFeatures.length, wells.length, perimeter.length)) {
        return;
    }

   // Obtain the map view extents for bounding the grid a second time
    mapView = map.getView().calculateExtent(map.getSize());

    //Split the coordinate arrays into separate X and Y coordinate arrays

    pCoords = perimeter.toString();
    wCoords = wells.toString();

    pCoords = pCoords.split(",");
    wCoords = wCoords.split(",");
    //console.log(wCoords);

    // Perimeter coordinates by X and Y
    i = 0;
    iX = 0;
    iY = 0;
    do {
        if (!isOdd(i)){ //even
            pXCoords[iX] = parseFloat(pCoords[i]);
            i++;
            iX++;
        }

        else {
            pYCoords[iY] = parseFloat(pCoords[i]);
            i++;
            iY++;
        }
    }
    while (i < pCoords.length);

   // Well coordinates by X and Y
   //reinitialize counters
    i = 0;
    iX = 0;
    iY = 0;
    do {
        if (!isOdd(i)){
            wXCoords[iX] = parseFloat(wCoords[i]);
            i++;
            iX++;
        }

        else {
            wYCoords[iY] = parseFloat(wCoords[i]);
            i++;
            iY++;
        }
    }
    while (i < wCoords.length);

    // Map View Extent coordinates

    mapXCoords[0] = mapView[0];
    mapYCoords[0] = mapView[1];
    mapXCoords[1] = mapView[2];
    mapYCoords[1] = mapView[3];


    //This section defines the cell size based on a percentage for the area selected
    //the shortest dimension is what determines the cellsize
    var scale = 0.1;
    var cellSide = 0.0;

    //console.log("Getting cellSide");

    if (Math.abs(pXCoords[0]-pXCoords[1]) > Math.abs(pYCoords[0]-pYCoords[1])){
        cellSide = Math.abs(pXCoords[0]-pXCoords[1])*scale;
    }
    else if (Math.abs(pXCoords[0]-pXCoords[1]) < Math.abs(pYCoords[0]-pYCoords[1])) {
        cellSide = Math.abs(pYCoords[0]-pYCoords[1])*scale;
    }
    else {
        cellSide = cellSide + Math.abs(pXCoords[0]-pXCoords[1])*scale;
    }

    var waterTableRegional = [];
    var levels = [];
    var Contours = [];
    var long, lat;

	$.ajax({
		type: 'GET',
		url: 'generate-water-table',
		dataType: 'json',
		data: {
			'xIndex': JSON.stringify(mapXCoords),
			'yIndex': JSON.stringify(mapYCoords),
			'wXCoords': JSON.stringify(wXCoords),
			'wYCoords': JSON.stringify(wYCoords),
			'cellSide': JSON.stringify(cellSide),
			'initial': JSON.stringify(iwte.value),
			'bedrock': JSON.stringify(bedrock.value),
			'q': JSON.stringify(q.value),
			'k': JSON.stringify(k.value),
			},
			success: function (data){
//					console.log(data)
					waterTableRegional = (JSON.parse(data.local_Water_Table));
					var raster_elev_mapView = {
						'type': 'FeatureCollection',
						'crs': {
							'type': 'name',
							'properties':{
								'name':'EPSG:4326'
								}
						},
						'features': waterTableRegional
					};

					levels = (JSON.parse(data.heads));

					Contours = (JSON.parse(data.contours));
					var contourLines = {
						'type': 'FeatureCollection',
						'crs': {
							'type': 'name',
							'properties': {
								'name':'EPSG:4326'
							}
						},
						'features': Contours
					}

					addWaterTable(raster_elev_mapView,"Water Table");
					addDewateredLayer(raster_elev_mapView,"Dewatered Region(s)");
					//addContours(contourLines,levels,"Elevation Contours");
					}
			});
};
//  #################################### Add the new water table contours to the map ###################################
function addContours(contourLines,levels,titleName){

    getStyleColor = function(value) {
        if (value = levels[0])
            return (165,42,42,1);		//	Brown, Hex:#A52A2A
        else if (value = levels[1])
            return [191,0,23, 1];		//	Red, Hex:BF0017
        else if (value = levels[2])
            return [196,87,0,1];		//	Orange, Hex:C45700
        else if (value = levels[3])
            return [255,165,0,1];		//	Light Orange, Hex:ffa500
        else if (value = levels[4])
            return [255,255,0,1];		//	Yellow, Hex:FFFF00
        else if (value = levels[5])
            return [0,255,0,1];			//	Green
        else if (value = levels[6])
            return [0,218,157,1];		//	Turqoise(ish), Hex:00DA9D
        else if (value = levels[7])
            return [0,158,223,1];		//	Lighter Blue, Hex:009EDF
        else if (value = levels[8])
            return [1,107,231,0.7];		//	Light Blue, Hex:016BE7
		else
			return [0,32,229,0.7];		//	Blue, Hex:0020E5
    };

    //	Reads in the contour lines as GeoJSON objects and creates an openlayers vector object
    var collection = contourLines;
    var format = new ol.format.GeoJSON();
    var vectorSource = new ol.source.Vector({
        features: format.readFeatures(collection,
        {featureProjection:"EPSG:4326"})
        });

	//	Default style
	var defaultStyle = new ol.style.Style({
	stroke: new ol.style.Stroke({
	color: [220,220,220,0.7],
	width: 1
	})
	});

};

//  #################################### Add the new water table raster to the map #####################################

function addWaterTable(raster_elev,titleName){

    var getStyleColor;
    var map;
    var i;

    getStyleColor = function(value) {
        if (value > Number(dwte.value)+(Number(dwte.value)-Number(bedrock.value))*0.375)
            return [0,32,229,0.7];       //Blue, Hex:0020E5
        else if (value > Number(dwte.value)+(Number(dwte.value)-Number(bedrock.value))*0.25)
            return [1,107,231,0.7];       //Light Blue, Hex:016BE7
        else if (value > Number(dwte.value)+(Number(dwte.value)-Number(bedrock.value))*0.125)
            return [0,158,223,0.7];     //Lighter Blue, Hex:009EDF
        else if (value > dwte.value)
            return [0,218,157,0.7];       //Turqoise(ish), Hex:00DA9D
        else if (value > Number(dwte.value)-(Number(dwte.value)-Number(bedrock.value))*0.125)
            return [0,255,0,0.7];         //Green
        else if (value > Number(dwte.value)-(Number(dwte.value)-Number(bedrock.value))*0.25)
            return [255,255,0,0.7];       //Yellow, Hex:FFFF00
        else if (value > Number(dwte.value)-(Number(dwte.value)-Number(bedrock.value))*0.375)
            return [196,87,0,0.7];       //Orange, Hex:C45700
        else if (value > Number(bedrock.value))
            return [191,0,23, 0.7];           //Red, Hex:BF0017
		else
			return [0,0,0,0.7];
    };

    var defaultStyle = new ol.style.Style({
        fill: new ol.style.Fill({
            color: [0,0,0,0.7]
        }),
        stroke: new ol.style.Stroke({
        color: [220,220,220,0.7],
        width: 1
        })
    });
    //This will be used to cache the style
    var styleCache = {};

    //the style function returns an array of styles for the given feature and resolution
    //Return null to hide the feature
    function styleFunction(feature, resolution){
        //get the elevation from the feature properties
        var elevation = feature.get('elevation');
        //if there is no elevation value or it's one we don't recognize,
        //return the default style
        if(!elevation) {
            return [defaultStyle];
            }
        //check the cache and create a new style for the elevation if it's not been created before.
        if(!styleCache[elevation]){
            var style_color = getStyleColor(elevation);
            styleCache[elevation] = new ol.style.Style({
                fill: new ol.style.Fill({
                    color: style_color
                    }),
                stroke: defaultStyle.stroke
                });
            }
    //at this point, the style for the current level is in the cache so return it as an array
        return [styleCache[elevation]];
    }

    var collection = raster_elev;
    var format = new ol.format.GeoJSON();
    //map.getLayers().item(2).getSource().addFeatures(format.readFeatures(collection, {featureProjection:"EPSG:4326"}))
    var vectorSource = new ol.source.Vector({
        features: format.readFeatures(collection,
        {featureProjection:"EPSG:4326"})
        });

    var display = true;

    var vector = new ol.layer.Image({
            tethys_legend_title: titleName,
            zIndex: 1,
            source: new ol.source.ImageVector({
                source: vectorSource,
                style: styleFunction,
            }),
        });

    // Make sure that the layer is not already existing, remove it if the layer does exist
    map = TETHYS_MAP_VIEW.getMap();
    for (i = 0; i < map.getLayers().getProperties().length ; i ++){
        if (map.getLayers().item(i).getProperties().tethys_legend_title === titleName)
            map.removeLayer(map.getLayers().item(i));
    }
    vector.tethys_legend_title = titleName;
    map.addLayer(vector);

    TETHYS_MAP_VIEW.updateLegend();

    map.getLayers().item(1).setZIndex(3);

    toggle_legend(true,1);

}

//  #################################### Add a layer symbolizing dewatered/not-dewatered ###############################

function addDewateredLayer(raster_elev,titleName){

    var getStyleColor;
    var map;
    var i;

    getStyleColor = function(value) {
        if (value <= Number(dwte.value))
            return [0,255,0,0.7];         //Green
		else if (value > Number(dwte.value))
            return [191,0,23, 0.7];       //Red, Hex:BF0017
		else
			return defaultStyle;
    };

    var defaultStyle = new ol.style.Style({
        fill: new ol.style.Fill({
            color: [0,0,0,0.7]
        }),
        stroke: new ol.style.Stroke({
        color: [220,220,220,0.7],
        width: 1
        })
    });
    //This will be used to cache the style
    var styleCache = {};

    //the style function returns an array of styles for the given feature and resolution
    //Return null to hide the feature
    function styleFunction(feature, resolution){
        //get the elevation from the feature properties
        var elevation = feature.get('elevation');
        //if there is no elevation value or it's one we don't recognize,
        //return the default style
        if(!elevation) {
            return [defaultStyle];
            }
        //check the cache and create a new style for the elevation if it's not been created before.
        if(!styleCache[elevation]){
            var style_color = getStyleColor(elevation);
            styleCache[elevation] = new ol.style.Style({
                fill: new ol.style.Fill({
                    color: style_color
                    }),
                stroke: defaultStyle.stroke
                });
            }
    //at this point, the style for the current level is in the cache so return it as an array
        return [styleCache[elevation]];
    }

    var collection = raster_elev;
    var format = new ol.format.GeoJSON();
    //map.getLayers().item(2).getSource().addFeatures(format.readFeatures(collection, {featureProjection:"EPSG:4326"}))
    var vectorSource = new ol.source.Vector({
        features: format.readFeatures(collection,
        {featureProjection:"EPSG:4326"})
        });

    var display = true;

    var vector = new ol.layer.Image({
            tethys_legend_title: titleName,
            zIndex: 1,
            source: new ol.source.ImageVector({
                source: vectorSource,
                style: styleFunction,
            }),
        });

    // Make sure that the layer is not already existing, remove it if the layer does exist
    map = TETHYS_MAP_VIEW.getMap();
    for (i = 0; i < map.getLayers().getProperties().length ; i ++){
        if (map.getLayers().item(i).getProperties().tethys_legend_title === titleName)
            map.removeLayer(map.getLayers().item(i));
    }
    vector.tethys_legend_title = titleName;
    vector.setVisible(false);
    map.addLayer(vector);

    TETHYS_MAP_VIEW.updateLegend();

    $('a.display-control').on("click", function(){
        $(function() {
            var map = TETHYS_MAP_VIEW.getMap();
            if (!!map.getLayers().item(2)){
                toggle_legend(map.getLayers().item(2).getProperties().visible,1);
            };
            if (!!map.getLayers().item(3)){
                toggle_legend(map.getLayers().item(3).getProperties().visible,2);
            }
        })
    });

}

//  #################################### Toggle Color Legend On/Off ####################################################
function toggle_legend(boolean,layer){
//    var ele = "";
    var i;

    i = 1;
	if (layer == 1){
		document.getElementById(String(i)).innerHTML = Math.round(Number(Number(dwte.value)+Number(1)+((Number(dwte.value)-Number(bedrock.value))*0.375)));
		i = i+1;
		document.getElementById(String(i)).innerHTML = Math.round(Number(Number(dwte.value)+((Number(dwte.value)-Number(bedrock.value))*0.375))) + "-" + Math.round(Number(Number(dwte.value)+((Number(dwte.value)-Number(bedrock.value))*0.25)));
		i = i+1;
		document.getElementById(String(i)).innerHTML = Math.round(Number(Number(dwte.value)+((Number(dwte.value)-Number(bedrock.value))*0.25))) + "-" + Math.round(Number(Number(dwte.value)+((Number(dwte.value)-Number(bedrock.value))*0.125)));
		i = i+1;
		document.getElementById(String(i)).innerHTML = Math.round(Number(Number(dwte.value)+((Number(dwte.value)-Number(bedrock.value))*0.125))) + "-" + Math.round(Number(dwte.value));
		i = i+1;
		document.getElementById(String(i)).innerHTML = Math.round(dwte.value) + "-" + Math.round(Number(Number(dwte.value)-((Number(dwte.value)-Number(bedrock.value))*0.125)));
		i = i+1;
		document.getElementById(String(i)).innerHTML = Math.round(Number(Number(dwte.value)-((Number(dwte.value)-Number(bedrock.value))*0.125))) + "-" + Math.round(Number(Number(dwte.value)-((Number(dwte.value)-Number(bedrock.value))*0.25)));
		i = i+1;
		document.getElementById(String(i)).innerHTML = Math.round(Number(Number(dwte.value)-((Number(dwte.value)-Number(bedrock.value))*0.25))) + "-" + Math.round(Number(Number(dwte.value)-((Number(dwte.value)-Number(bedrock.value))*0.375)));
		i = i+1;
		document.getElementById(String(i)).innerHTML = Math.round(Number(Number(dwte.value)-((Number(dwte.value)-Number(bedrock.value))*0.375))) + "-" + Number(Number(1)+Number(bedrock.value));
		i = i+1;
		document.getElementById(String(i)).innerHTML = Number(bedrock.value);
		i = i+1;

        var ele = document.getElementById("colorLegend");

        if (boolean == true)
            ele.style.display = "block";
        else
            ele.style.display = "none";
    }
    else if (layer == 2){

        var ele = document.getElementById("dewatered");

        if (boolean == true)
            ele.style.display = "block";
        else
            ele.style.display = "none";

    }
};

//  #################################### Add Contour Legend ############################################################


//Create public functions to be called in the controller
var app;
app = {dewater: dewater}






