import arcpy

arcpy.env.overwriteOutput = True
arcpy.env.scratchWorkspace = "F:\\AllSemesters\\Fall13\Geog497C\\FinalProject\\Geog497CFinal\\Scratch"

# Input workspace folder as parameter and set 
# the environment workspace to it
inputFolder = arcpy.GetParameterAsText(0)			# input folder
if not inputFolder:
	inputFolder = "F:\\AllSemesters\\Fall13\\Geog497C\\Geog497CFinal"
arcpy.env.workspace = inputFolder

# Input various files needed
dem = arcpy.GetParameterAsText(1)					# DEM file for elevation
if not dem:
	dem = "F:\\AllSemesters\\Fall13\\Geog497C\\Geog497CFinal\\PHIL5FTDEM.images\\rd_52462850.img"

hospitals = arcpy.GetParameterAsText(2)				# Hospitals feature class
if not hospitals:
	hospitals = "F:\\AllSemesters\\Fall13\\Geog497C\\Geog497CFinal\\HospitalsClipped.shp"

hydro = arcpy.GetParameterAsText(3)					# Hydrography feature class
if not hydro:
	hydro = "F:\\AllSemesters\\Fall13\\Geog497C\\Geog497CFinal\\HydroPolyClip.shp"

population = arcpy.GetParameterAsText(4)			# Population layer
if not population:
	population = "F:\\AllSemesters\\Fall13\\Geog497C\\Geog497CFinal\\Blocks\\BlocksClipped.shp"


# Begin raster calculations

# Check out Arcpy Spatial Analyst Extension
arcpy.CheckOutExtension("Spatial")
'''
# Calculate the high, med, and low elevation thresholds
try:

        demRaster = arcpy.sa.Raster(dem)
        elevMin = demRaster.minimum
        arcpy.AddMessage(elevMin)
        elevMax = demRaster.maximum
        arcpy.AddMessage(elevMax)
        elevDiff = elevMax - elevMin
        arcpy.AddMessage(elevDiff)
        numRanks = 4	# 4 Risk Ranks: High, Med, Low, None

        # Threshold values based on risk level, the lower the
        # elevation, the higher the present risk
        elevClassSize = elevDiff / numRanks
        threshHighVal = elevMin + elevClassSize
        threshMedVal = threshHighVal + elevClassSize
        threshLowVal = threshMedVal + elevClassSize
                
        print "Raster calculations complete"
        arcpy.AddMessage("Raster calculations complete")

except:

        print "Could not complete DEM calculations\n" + arcpy.GetMessages()
        arcpy.AddError("Could not complete DEM calculations")
        arcpy.AddMessage(arcpy.GetMessages())
        
# Elevation Remapping
try:
        
        elevMapping = [[elevMin, threshHighVal, 3],[threshHighVal, threshMedVal, 2],[threshMedVal, threshLowVal, 1],[threshLowVal, elevMax, 0]]
        elevRemapRange = arcpy.sa.RemapRange(elevMapping)
        rankedElevRaster = arcpy.sa.Reclassify(demRaster, 'VALUE', elevRemapRange)

        # Save the ranked raster
        rankedElevRaster.save(inputFolder + '/elevRank.img')

        print "Elevation remapping complete"
        arcpy.AddMessage("Elevation remapping complete")

except:

        print "Could not complete elevation remapping\n" + arcpy.GetMessages()
        arcpy.AddError("Could not complete elevation remapping")
        arcpy.AddMessage(arcpy.GetMessages())
        



# Multi-ring buffer analysis and conversion to raster for hospitals layer
try:

        arcpy.MultipleRingBuffer_analysis(hospitals, inputFolder + '/hosp_buffered.shp', [0.25, 0.75, 1.50, 10.0], 'miles', 'distance')
        arcpy.PolygonToRaster_conversion (inputFolder + '/hosp_buffered.shp', 'distance', inputFolder + '/hosp_rast.img')

        print "Multi-ring buffer and conversion to raster for hospitals complete"
        arcpy.AddMessage("Multi-ring buffer for hospitals complete")

except:

        print "Could not complete multi-ring buffer and conversion to raster for hospitals\n" + arcpy.GetMessages()
        arcpy.AddError("Could not complete multi-ring buffer and conversion to raster for hospitals")
        arcpy.AddMessage(arcpy.GetMessages())

# Hospital remapping         
try:    

        arcpy.CalculateStatistics_management(inputFolder + '/hosp_rast.img')
        hospRaster = arcpy.sa.Raster(inputFolder + '/hosp_rast.img')
        hospMapping = [[0.25, 0], [0.75, 1], [1.50, 2], [10, 3]]
        hospRemapVal = arcpy.sa.RemapValue(hospMapping)
        rankedHospRaster = arcpy.sa.Reclassify(hospRaster, 'VALUE', hospRemapVal)

        # Save the ranked raster
        rankedHospRaster.save(inputFolder + '/rankHosp.img')

        print "Hospital buffer reclassification complete"
        arcpy.AddMessage("Hospital buffer reclassification complete")

except:

        print "Could not complete ospital buffer reclassification\n" + arcpy.GetMessages()
        arcpy.AddError("Could not complete ospital buffer reclassification")
        arcpy.AddMessage(arcpy.GetMessages())

# Multi-ring buffer analysis and conversion to raster for hydrography layer
try:    

        arcpy.MultipleRingBuffer_analysis(hydro, inputFolder + '/hydro_buffered.shp', [0.25, 0.75, 1.50, 10.00], 'miles', 'distance')
        arcpy.PolygonToRaster_conversion (inputFolder + '/hydro_buffered.shp', 'distance', inputFolder + '/hydr_rast.img')

        print "Multi-ring buffer analysis and conversion to raster for hydrography layer complete"
        arcpy.AddMessage("Multi-ring buffer analysis and conversion to raster for hydrography layer complete")

except:

        print "Could not complete multi-ring buffer analysis and conversion to raster for hydrography layer\n" + arcpy.GetMessages()
        arcpy.AddError("Could not complete multi-ring buffer analysis and conversion to raster for hydrography layer")
        arcpy.AddMessage(arcpy.GetMessages())

# Hydrogrpahy remapping
try:

        arcpy.CalculateStatistics_management(inputFolder + '/hydr_rast.img')
        hydroRaster = arcpy.sa.Raster(inputFolder + '/hydr_rast.img')
        hydroMapping = [[0.25, 0], [0.75, 1], [1.50, 2], [10.00, 3]]
        hydroRemapVal = arcpy.sa.RemapValue(hydroMapping)
        rankedHydroRaster = arcpy.sa.Reclassify(hydroRaster, 'VALUE', hydroRemapVal)

        # Save the ranked raster
        rankedHydroRaster.save(inputFolder + '/rankHydr.img')

        print "Hydrography reclassification complete"
        arcpy.AddMessage("Hydrography reclassification complete")

except:

        print "Could not complete multi-ring buffer analysis and conversion to raster for hydrography layer\n" + arcpy.GetMessages()
        arcpy.AddError("Could not complete multi-ring buffer analysis and conversion to raster for hydrography layer")
        arcpy.AddMessage(arcpy.GetMessages())

# Perform population analysis
try:

        arcpy.PolygonToRaster_conversion (inputFolder + '/Blocks/BlocksClipped.shp', 'POP10', inputFolder + '/pop_ras.img')
        popRaster = arcpy.sa.Raster(inputFolder + '/pop_ras.img')

        print "Hydrography reclassification complete"
        arcpy.AddMessage("Hydrography reclassification complete")

except:

        print "Could not complete DEM reclassification\n" + arcpy.GetMessages()
        arcpy.AddError("Could not complete DEM calculations")
        arcpy.AddMessage(arcpy.GetMessages())        

# Create threshold values based on risk level, the lower the elevation, the higher the present risk
try:

        popMin = popRaster.minimum
        print popMin
        popMax = popRaster.maximum
        print popMax
        popDiff = popMax - popMin
        numPopRanks = 4

        popClassSize = popDiff / numPopRanks
        threshHighVal = 3 * popClassSize
        threshMedVal = 2 * popClassSize
        threshLowVal = popClassSize

        print "Population classification complete"
        arcpy.AddMessage("Population classification complete")

except:

        print "Could not complete population classification\n" + arcpy.GetMessages()
        arcpy.AddError("Could not complete population classification")
        arcpy.AddMessage(arcpy.GetMessages())

# Population remapping and conversion to raster
try:

        popMapping = [[popMin, threshLowVal, 0],[threshLowVal, threshMedVal, 1],[threshMedVal, threshHighVal, 2],[threshHighVal, popMax + 1, 3]]
        popRemapRange = arcpy.sa.RemapRange(popMapping)
        rankedPopRaster = arcpy.sa.Reclassify(popRaster, 'VALUE', popRemapRange)

        # Save Population Raster
        rankedPopRaster.save(inputFolder + '/rankPop.img')

        print "Population remapping and conversion to raster complete"
        arcpy.AddMessage("Population remapping and conversion to raster complete")

except:

        print "Could not complete population remapping and conversion to raster\n" + arcpy.GetMessages()
        arcpy.AddError("Could not complete population remapping and conversion to raster")
        arcpy.AddMessage(arcpy.GetMessages())


# DO MAP ALGEBRA
try:

        finalRankedRaster = rankedHydroRaster + rankedHospRaster + rankedElevRaster + rankedPopRaster
        finalRankedRaster.save(inputFolder + '/finalRanking.img')

        print "Map algebra complete"
        arcpy.AddMessage("Map algebra complete")

except:

        print "Could not complete map algebra\n" + arcpy.GetMessages()
        arcpy.AddError("Could not complete map algebra")
        arcpy.AddMessage(arcpy.GetMessages())

# Create threshold values for map algebra
try:

        algebraMin = finalRankedRaster.minimum
        algebraMax = finalRankedRaster.maximum
        algebraDiff = algebraMax - algebraMin
        numAlgebraRanks = 4

        algebraClassSize = algebraDiff /numAlgebraRanks
        threshHighVal = 3 * algebraClassSize
        threshMedVal = 2 * algebraClassSize
        threshLowVal = algebraClassSize

        print "Algebra classifcation complete"
        arcpy.AddMessage("Algebra classifcation complete")

except:

        print "Could not complete Algebra classifcation\n" + arcpy.GetMessages()
        arcpy.AddError("Could not complete Algebra classifcation")
        arcpy.AddMessage(arcpy.GetMessages())
'''
# Reclassify Map Algebra
try:
        finalRaster = arcpy.sa.Raster(inputFolder + '/finalRanking.img')
        MapAlgebraMapping = [[0,3, 0],[3,6, 1],[6,10, 2],[10,13, 3]]
        AlgebraRemapRange = arcpy.sa.RemapRange(MapAlgebraMapping)
        rankedAlgebraRaster = arcpy.sa.Reclassify(finalRaster, 'VALUE', AlgebraRemapRange)

        # Save Population Raster
        rankedAlgebraRaster.save(inputFolder + '/rankAl.img')

        print "Algebra reclassifcation complete"
        arcpy.AddMessage("Algebra reclassifcation complete")

except:

        print "Could not complete Algebra reclassifcation\n" + arcpy.GetMessages()
        arcpy.AddError("Could not completeAlgebra reclassifcation")
        arcpy.AddMessage(arcpy.GetMessages())

# Convert Map Algebra into Polygon
try:
        arcpy.RasterToPolygon_conversion(rankedAlgebraRaster, inputFolder + '/Zones.shp')

        print "Raster to polygon conversion complete"
        arcpy.AddMessage("Raster to polygon conversion complete")

except:

        print "Could not complete Raster to polygon conversion\n" + arcpy.GetMessages()
        arcpy.AddError("Could not complete Raster to polygon conversion")
        arcpy.AddMessage(arcpy.GetMessages())

# Add Risk Field to Algebra and classify
print "Performing data management"
arcpy.AddField_management(inputFolder + '/Zones.shp', "RiskZones", "STRING")

with arcpy.da.UpdateCursor(inputFolder + '/Zones.shp', ["GRIDCODE", "RiskZones"]) as rows:
        for row in rows:

                # Select by attricute and classify Zones
                if row[0] == 0:                      
                    row[1]= 'No Risk'
                    rows.updateRow(row)
                elif row[0] == 1:
                    row[1]= 'Low Risk'
                    rows.updateRow(row)
                elif row[0] == 2:
                    row[1] = 'Medium Risk'
                    rows.updateRow(row)
                elif row[0] == 3:
                    row[1] = 'High Risk'
                    rows.updateRow(row)

print "Data management complete"
arcpy.AddMessage("Data management complete")

print "Flood Risk Analysis Complete!"
arcpy.AddMessage("Flood Risk Analysis Complete!")



