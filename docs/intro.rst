Introduction
============

Why Use Webmaps as Templates?
-----------------------------

When the GIS team wants to share spatial data with a general audience, we publish the layers as a feature service, either on AGOL or our Enterprise SDE instance.  Within ArcGIS Pro, we can tweak the symbology, the labeling, and the popup info, so why does a Webmap become necessary?  As it turns out, many of the settings in ArcGIS Pro are not compatible with viewing on the web.  Complex feature symbology may fail to build, and will fall back to a default color and symbol type that is probably not what you want (this is particularly common when using hatching).  ArcGIS Pro uses the MapLex labeling engine, whereas the online web server does not.  Since we want our users to consume our published services via Webmaps, using a Webmap as a template ensures that the symbol and label definitions we select will appear and function correctly in their destination environment.

In addition, there are several "server-side" settings that can only be adjusted once the service is imported into a Webmap.  Enabling popups, and making the fields of individual layers searchable, are examples of settings that can only be set after importing into a Webmap.  Saving these settings in a template Webmap makes it easy to reference the implementation and reproduce the build when making a new map.  The use of templates reduces the need for manually copying maps and ajusting settings using the AGOL GUI interface, saving time and clicks.


