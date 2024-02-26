Making Maps
===========

As discussed in :doc:`intro`, a published service is often not sufficient for producing a quality web map.  Differences in how symbology gets rendered in a web environment, as well as how popups and labels are displayed, can require "server-side" configuration.  Perhaps you are using a service published by another agency, and want to alter the symbology or labeling for your site.  Generally, we recommend making a template for each service that you want to use.  Use the template to configure the web map experience, using the GUI provided in the ESRI Map Viewer.  Each service published by the city should have a reference template showing how to render each layer.  To build a new web map, we first pull in these reference templates, and then compose our new map from the pieces present in the templates.

Here we present some examples of how to use the ``mapmakers`` package to prepare a new map from a set of templates.

From Template to Map
--------------------

The most simple case is creating a map from an existing template.  In this instance we want to make a new map with exactly the same layers and configuration as the original template.  As in the previous chapter, we will be working from the *demo.py* project in the *examples* folder.  Here we define a function called *property*:

.. code-block:: python

    def property(template):
        return template.template["property"].into_items().group("Property")

This functions takes an argument called *template*, which must be an instance of the *Templates* class.  As covered in :doc:`template_use`, we can create this template either from a workbook using *Templates.from_workbook* or directly from the item IDs using *Templates.from_obj*.

The syntax ".template['property']" selects the template named "property" from the *Templates* instance, so the resulting object is of type *Template*.  The *into_items* method converts the *Template* object into the ``mapmakers`` *Items* class.  The *Items* class has a property field called *items* that holds a list with elements of class *Item*, the ``mapmakers`` class for map items.  Each *Item* contains information related to a particular layer.

The *group* method takes an *Item* or *Items* and places them into a map group.  The method takes a single argument specifying the display name of the group, in this case "Property".  The line as a whole takes the layers in the "property" template, converts them into map items, and places these layers into a group called "Property", preserving the original order of the layers.

We will use the *Map* class to build a web map from the *Group* object.  Instantiating the *Map* class requires three arguments.  The first argument is the item ID of the target web map.  The *arcgis* Python API does not provide a function for creating a new web map, so we must pass in an existing Item ID.  We have created a web map called "test_demo_example" that we will reference for this example.

.. code-block:: python

   demo_id = "6b81b63a99e74192ac00c3a53b88ca27"

For the city web viewer, we use six different web maps.  First, we have a map for test builds.  We have a different version of the web viewer for public and staff.  We also have a separate map that provides an editable version of various layers.  Finally, we have a backup map for both the staff and public versions, so that we can build a new map and swap it into the viewer app without experiencing down time.  In the *grants_pass* folder of the *examples* directory, the project *web_viewer.py* includes an *Enum* listing the different target Item IDs.

.. code-block:: python

    class Target(Enum):
        TEST = "2bc59679ad4040f4b7eb9ebec358152b"
        STAFF = "2c76b256e6954677802813291d22a2b9"
        STAFF1 = "199ca9a74d824a2287895cd736394138"
        PUBLIC = "8b104a6cfc774ba29cd873edf2bbef73"
        PUBLIC1 = "df37a2bec8554462a4e33d02bea239dc"
        EDITOR = "54738cddf51648ad99ba0ec5dfff2625"

We can then refer to a specific target map, referencing a particular variant's value.

.. code-block:: python

   mp = m.Map(Target.TEST.value, property(tmp), gis)

Within the *demo.py* project, we can use the *demo_id*:

.. code-block:: python

   mp = m.Map(demo_id, property(tmp), gis)

The second argument required to create a new instance of the *Map* class is the layer data for map, in this case the output of the *property* function.  The *Map* class is flexible enough to convert objects of class *Item*, *Items*, *Layer*, *Layers* and *Group* into a *Map* object, as well as lists containing these classes.  We will provide some examples below.

The final argument required to create an instance of the *Map* class is an authenticated GIS connection.  We have used *gis* to alias the *GIS_CONN* connection created by our login script.

The *Map* class includes a *build* method.  The *build* method will clear the target web map of any existing layers and then populate the map with the layer information stored in the *Map* object.  Executing the *build* method can take a moment, and will complete silently.  Add a logging message after the *build* call if you want to confirm completion.

.. code-block:: python

   mp.build()
   logging.info("Target map updated.")

Making a new map exactly like the template map may not sound like a practical use case, but keep in mind that this methodology applies to groups within a map as well.  If you are only updating a couple layers on a large map like the web viewer, and the majority of groups have not changed, then you can build these group layers directly from their templates with minimal effort.

Nesting A Group Layer
---------------------

Group layers are an important tool for organizing layers into sensible categories for easier navigation. One of my original motivations for writing this package came from my frustration at organizing the layers of an ArcGIS Pro project into groups, only to have those group categories disappear when published as a service.  The initial "killer feature" of the ``mapmakers`` package was the ability organize layers into groups programmatically using code, instead of manually through the ESRI Map Viewer GUI. 

The *boundaries* function in *demo.py* illustrates the method for nesting a group layer within another group:

*demo.py*

.. code-block:: python

    def boundaries(template):
        plss = template.template["plss"].into_items().group("PLSS")
        boundaries = template.template["boundaries"].into_items().layers()
        logging.info("Appending PLSS")
        boundaries = boundaries.append(plss).group("Boundaries")
        return boundaries

First we create a group layer called "PLSS" from the template called "plss".  As with the "property" example, we convert the *Template* into an *Items* object using the *into_items* method, and then enclose it in a group layer using the *group* method.  The second line of the function creates a variable called *boundaries* by accessing the template "boundaries" and converting it into an *Items* object with the *into_items* method.  Instead of placing the results immediately into a group, we want to add the PLSS group to the list of layers included in the "Boundaries" group, so we call the *layers* method.  The *layers* method converts members of the *Items* class into the *Layers* class.

Why do we need to covert *boundaries* from the *Items* class into the *Layers* class?  The *Item* class provides fields and methods for modifying aspects of the target layer, like the title or layer visibility, and serves as a recipe for how to create the map layer.  The *Layer* class converts these instructions into a JSON dictionary that describes the layer details in a format that matches the ESRI specification for web maps.  When we create a group layer, first we must convert all the items within the group into *Layer* objects, and then embed this information inside the definition of the group layer.  The *Items* class can only contain references to objects of the *Item* class, but the *Layers* class can contain references to either a *Layer* class or a *Group*, so to create a nested group we first covert the *Items* into *Layers*, and then append the *Group* to the list of layers.

We have implemented the *append* and *extend* methods for the *Layers* class, to make it easier to add classes of different type to a list of layers.  When calling *append* or *extend* on the layers class directly, the ``mapmakers`` package will keep the search fields and layer data synchronized when inserting new layers.  If you were to append a layer by directly accessing the *layers* property in the *Layers* class, then you would have to remember to also grab the corresponding search terms in the *search* property and append that as well.  It is safer and easier to call *append* or *extend* from the *Layers* class when performing operations like nesting a group.  In the example above we append the "PLSS" group to the layers in *boundaries*, and then enclose these layers in a new group called "Boundaries".

There is a special case to cover when combining *Group* and *Layer* classes.  When working with a *Layers* object, you can use *append* or *extend* to add additional layers to the object, but what if the first layer (the bottom of the render stack) needs to be a group?  If you try to *append* or *extend* additional layers to a *Group* object, you will get an error.

.. code-block:: python

   # won't work because plss is type *Group*
   plss = plss.append(boundaries).group("Boundaries")

In order to make this work, you must convert the *plss* object into the *Layers* class using the *into_layer* method:

.. code-block:: python

   # works because plss is type *Layers*
   plss = plss.into_layer()
   plss = plss.append(boundaries).group("Boundaries")

Raster Layers
-------------

Raster layers require special treatment because the JSON representation of the layer used by ESRI has distinct differences from the representation of a vector layer. In order to format these layers correctly, you must convert them into the *Layers* class using the *rasters* method.  To illustrate this, let us take a look at the *aerials* function in *demo.py*:

.. code-block:: python

    def aerials(template):
        imagery = template.template["aerials"].into_items().rasters()
        imagery = imagery.group("Aerials")
        return imagery

Once you have transformed raster data from the *Items* class into the *Layers* class using the *rasters* method, then you can treat it like any other group or layer data.  If you have only a single layer of raster data, use the *raster* method to transform the *Item* object into a *Layer* object:

.. code-block:: python

   imagery = template.template["aerials"].items["aerials_0"].into_item().raster()

Cherry-Picking Layers
---------------------

This section explains how to compose individual layers into a web map.  Use the techniques in this section to select a single layer or a subset of layers from a published service for use in your map.  To illustrate the workflow, we have added the *cherry_pick* function to *demo.py*:

.. code-block:: python

    def cherry_pick(t: m.Templates):
        # cherry pick an item using the item name
        city_limits = t.template["boundaries"].items["boundaries_5"].into_item()
        prop = t.template["property"].into_items()
        # index into *items* to cherry pick multiple layers
        prop.items = prop.items[1:4]
        quarters = t.template["plss"].into_items()
        # the type of the *items* property is a list
        # to cherry pick a single item, pass it in a list
        quarters.items = [quarters.items[0]]
        lyrs = prop
        # use extend to add a list of items to the *items* field
        lyrs.items.extend(quarters.items)
        # use append to add a single item to the *items* field
        lyrs.items.append(city_limits)
        mp = m.Map(demo_id, lyrs, gis)
        mp.build()
        logging.info("Target map updated.")

The easiest way to select a single layer from a template is to use the item name associated with the layer.  As discussed in :doc:`template_use`, you can set the item names of layers in a template either using the *with_names* method, or by editing the *name* column in the template workbook.  If you do not manually set item names, then the names will layers will automatically be set to the template name followed by an underscore and the layer index, beginning at zero.  In the *cherry_pick* example, we used auto-naming for the *boundaries* template.  Examining the workbook in "examples/demo/workbook.csv", we can see that the name for the City Limits layer is "boundaries_5".  By inserting the item name in brackets after the property *items*, we can select that particular item from the template.

You can create a new *Items* object from any list where the elements are of class *Item*.

.. code-block:: python

   county_line = t.template["boundaries"].items["boundaries_0"].into_item()
   gpid = t.template["boundaries"].items["boundaries_1"].into_item()
   reserve = t.template["boundaries"].items["boundaries_2"].into_item()
   wards = t.template["boundaries"].items["boundaries_3"].into_item()
   ugb = t.template["boundaries"].items["boundaries_4"].into_item()
   city_limits = t.template["boundaries"].items["boundaries_5"].into_item()
   # create an *Items* object from a list of *Item* objects
   boundaries = m.Items([county_line, gpid, reserve, wards, ugb, city_limits])
   # results are identical to this
   boundaries_1 = t.template["boundaries"].into_items()
   assert boundaries == boundaries_1

Since the *items* property in the *Items* class holds a list of *Item* objects, when you slice into the list to create a subset, the result is an *Items* object that holds only the items you have subset.

.. code-block:: python

   subset = t.template["boundaries"].into_items()
   # subset layer at index 0, 1 and 2
   subset.items = subset.items[0:3]
   county_line = t.template["boundaries"].items["boundaries_0"].into_item()
   gpid = t.template["boundaries"].items["boundaries_1"].into_item()
   reserve = t.template["boundaries"].items["boundaries_2"].into_item()
   # identical to subset
   subset_1 = m.Items([county_line, gpid, reserve])
   assert subset == subset_1

If you want to pull a single layer out of an *Items* object, you will need to wrap it in a list, because the type of the *items* property is a list.

.. code-block:: python

   subset = t.template["boundaries"].into_items()
   subset.items = [subset.items[0]]
   # This is the same as calling into the item by name
   county_line = t.template["boundaries"].items["boundaries_0"].into_item()
   assert subset == county_line

Customizing Layers
------------------

The *Item* class allows you to customize the url, title, visibility or opacity of the resulting layer.

* To change the url source for the layer, set the *url* property to the new target path.
* To change the title, set the *title* property to the desired display title.
* To change the visibility of the layer, set the *visible* property to `True` to make the layer visible, and `False` to make it invisible by default.  The ``mapmakers`` package sets the visiiblity of layers to `False` by default, so you will only need to use the *visible* property to set the visibility to `True`.
* To change the opacity of a layer, set the *opacity* property to a number between zero and one, where the proportion represents the percent of opacity in the resulting layer.

.. code-block:: python

   county_line = t.template["boundaries"].items["boundaries_0"].into_item()
   # change url source to internal portal
   county_line.url = "https://gisserver.grantspassoregon.gov/server/rest/services/city_boundaries/MapServer/7"
   county_line.title = "County Line"
   # visible defaults to False in mapmakers
   county_line.visible = True
   # opacity defaults to 0.5 in mapmakers
   county_line.opacity = 0.9

In the city web viewer, we use the *title* property to change the display title of the assessors taxlots layer from "Assessor Taxlots" to "Taxlots (County)" to emphasis that the data does not belong to the city.  We also use the *visible* property to make the city limits and the urban growth boundary visible by default.

Now you are familiar with all of the classes and methods we use to build the city web viewer.  You should have sufficient understanding to read and understand the build script at "*examples/grants_pass/web_viewer.py*".  Congratulations!  If you have questions or suggestions, feel free to contact us at gis@grantspassoregon.gov.
