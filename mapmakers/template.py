from dataclasses import dataclass
from pathlib import Path, PurePath
import mapmakers
import arcgis
from arcgis.gis import GIS
from arcgis.mapping import WebMap
import json
import logging
import pandas
import progressbar
import uuid


@dataclass
class TemplateItem:
    """
    The ``TemplateItem`` class holds display information about a specific layer from an ArcGIS Online web map.
    """

    _title: str
    _group_name: str
    _item_name: str | None
    _layer_definition: dict | None
    _popup_info: dict | None
    _url: str | None
    _search: list | None
    _id: uuid.UUID

    __slots__ = (
        "_title",
        "_group_name",
        "_item_name",
        "_layer_definition",
        "_popup_info",
        "_url",
        "_search",
        "_id",
    )

    def __init__(
        self,
        title: str,
        group_name: str,
        item_name: str | None,
        layer_definition,
        popup_info,
        url: str | None,
        search: list | None = [],
    ):
        self._title = title
        self._group_name = group_name
        self._item_name = item_name
        match type(layer_definition).__name__:
            case "NoneType":
                self._layer_definition = None
            case "float":
                self._layer_definition = None
            case "str":
                logging.debug("Reading def: %s", layer_definition)
                if layer_definition is not None and layer_definition != "nan":
                    self._layer_definition = layer_definition
                else:
                    self._layer_definition = None
            case "dict":
                self._layer_definition = layer_definition
            case _:
                logging.debug("Unexpected type: %s", type(layer_definition))
                self._layer_definition = None
        match type(popup_info).__name__:
            case "NoneType":
                self._popup_info = None
            case "float":
                self._popup_info = None
            case "str":
                logging.debug("Reading info: %s", popup_info)
                if popup_info is not None and popup_info not in ["nan", "null"]:
                    self._popup_info = popup_info
                else:
                    self._popup_info = None
            case "dict":
                self._popup_info = popup_info
            case _:
                logging.debug("Unexpected type: %s", type(popup_info))
                self._popup_info = None
        self._url = url
        self._search = search
        self._id = uuid.uuid4()

    @staticmethod
    def from_layer(layer: dict, group_name: str, searches: dict):
        """
        The *from_layer* method converts layer data from a web map into a ``TemplateItem`` object.  This method is an internal library function called by *Template.read*.

        :param layer: Layer data from the *layers* property of an *arcgis.mapping.WebMap* object.
        :type layer: dict
        :param group_name: The name of the template web map from which the layer originates.
        :type group_name: str
        :param searches: A dictionary with layer IDs as keys and search fields as values, produced by the *Template.get_search* method.
        :type searches: dict[str, list[str]]
        :return: A ``TemplateItem`` containing the map data of *layer*.
        :rtype: TemplateItem

        """
        logging.debug("Calling from layer.")
        title = "No title."
        if "title" in layer:
            title = str(layer["title"])
        logging.debug("Title is %s", title)
        item_name = None
        layer_definition = None
        if "layerDefinition" in layer:
            layer_definition = layer["layerDefinition"]
        logging.debug("Layer def is %s", layer_definition)
        popup_info = None
        if "popupInfo" in layer:
            popup_info = layer["popupInfo"]
        logging.debug("Popup def is %s", popup_info)
        url = layer["url"]
        logging.debug("Url is %s", url)
        search = []
        if "id" in layer:
            id = layer["id"]
            if id in searches:
                search.extend(searches[id])
        logging.debug("Search is %s", search)
        tmp = TemplateItem(
            title, group_name, item_name, layer_definition, popup_info, url, search
        )
        return tmp

    @staticmethod
    def from_parts(
        title: str,
        group_name: str,
        item_name: str,
        layer_definition: str,
        popup_info: str,
        url: str,
        search: list,
        id: uuid.UUID,
    ):
        """
        The *from_parts* method is an internal library function that assembles the values in different columns of a template workbook into a ``TemplateItem`` object.  Called by *Template.from_workbook*.

        :param title: The display title of the map layer.
        :type title: str
        :param group_name: The name of the parent template for the layer.
        :type group_name: str
        :param item_name: The human-readable nickname that serves as the key reference for the layer.
        :type item_name: str
        :param layer_definition: The JSON representation of the layer properties.
        :type layer_definition: str
        :param popup_info: The JSON representation of the popup definition for the layer.
        :type popup_info: str
        :param url: The url source of the layer.
        :type url: str
        :param search: A list of field names within the layer that should be searchable.
        :type search: list[str]
        :param id: A unique ID used internally by the library to track layers.
        :type id: uuid.UUID
        :return: A ``TemplateItem`` containing the map data of the layer.
        :rtype: TemplateItem
        """
        item = TemplateItem(
            title, group_name, item_name, layer_definition, popup_info, url, search
        )
        item.id = id
        return item

    @staticmethod
    def from_raster(raster: dict, group_name: str):
        """
        The *from_raster* method is an internal library function that converts raster data from a web map into a ``TemplateItem`` object.  Called by the *Template.read* method when the type of the layer is a raster.

        :param raster: Raster data from the *layers* property of an *arcgis.mapping.WebMap* object.
        :type raster: dict
        :param group_name: The name of the template web map from which the layer originates.
        :type group_name: str
        :return: A ``TemplateItem`` containing the map data of the layer.
        :rtype: TemplateItem
        """
        title = "No title."
        if "title" in raster:
            title = str(raster["title"])
        item_name = None
        if "id" in raster:
            item_name = str(raster["id"])
        logging.debug("Raster data type: %s", type(raster))
        layer_definition = raster
        popup_info = None
        url = raster["url"]
        return TemplateItem(
            title, group_name, item_name, layer_definition, popup_info, url
        )

    def into_item(self):
        """
        The *into_item* method converts a ``TemplateItem`` into a map ``Item``.  The url of the ``Item`` is set to the same url as the ``TemplateItem``.

        :return: A map ``Item`` containing the layer data of the ``TemplateItem``.
        :rtype: mapmakers.Item
        """
        url = "none"
        if self.url != None:
            url = self.url
        item = mapmakers.Item(url, self, title=self.title)
        return item

    def into_search(self, id: str) -> list[dict]:
        """
        The *into_search* method is an internal library function that takes the search fields listed in the *search* field of the ``TemplateItem`` and converts them into the JSON format recognized by ESRI web maps, so the resulting map can be searchable by the indicated field.  Because a layer can have multiple searchable fields or none, the index of elements in the *search* property does not necessarily match the index of layers in the *layers* property of the *Layers* class.  To ensure the search fields correspond to the correct map layer, we record the layer ID associated with a search field in the *get_search* method, and refer to the same layer ID when injecting search into the JSON definition of the map.

        :param id: The layer ID of the layer to be made searchable.
        :type id: str
        :return: A list containing dictionary elements structured to enable search on an ESRI WebMap.
        :rtype: list[dict]
        """
        fields = []
        if self.search is not None:
            for name in self.search:
                entry = {}
                entry.update({"id": id})
                field = {}
                field.update({"name": name})
                field.update({"exactMatch": False})
                field.update({"type": "esriFieldTypeString"})
                entry.update({"field": field})
                fields.append(entry)
        return fields

    @property
    def title(self):
        """
        The *title* property holds a string representation of the display title for the map layer.
        """
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    @property
    def group_name(self):
        """
        The *group_name* property holds a human-readable nickname for the parent ``Template`` of the ``TemplateItem``.
        """
        return self._group_name

    @group_name.setter
    def group_name(self, value: str):
        self._group_name = value

    @property
    def item_name(self):
        """
        The *item_name* property holds a human-readable nickname for the ``TemplateItem``.
        """
        return self._item_name

    @item_name.setter
    def item_name(self, value: str):
        self._item_name = value

    @property
    def layer_definition(self):
        """
        The *layer_definition* property holds a JSON representation of the layer definition for the ``TemplateItem``.
        """
        return self._layer_definition

    @layer_definition.setter
    def layer_definition(self, value: dict):
        self._layer_definition = value

    @property
    def popup_info(self):
        """
        The *popup_info* property holds a JSON representation of the popup info for the ``TemplateItem``.
        """
        return self._popup_info

    @popup_info.setter
    def popup_info(self, value: dict):
        self._popup_info = value

    @property
    def url(self):
        """
        The *url* property holds a string representation of the url source for the map layer.
        """
        return self._url

    @url.setter
    def url(self, value: str):
        self._url = value

    @property
    def search(self):
        """
        The *search* property holds a list of field names within a map layer that should be searchable.
        """
        return self._search

    @search.setter
    def search(self, value: list):
        self._search = value

    @property
    def id(self):
        """
        The *id* property holds a unique ID used internally to track map layers.
        """
        return self._id

    @id.setter
    def id(self, value: uuid.UUID):
        self._id = value


@dataclass
class Template:
    """
    The ``Template`` class holds map layer data from an ArcGIS Online web map.
    """

    _name: str
    _id: str
    _items: dict[str, TemplateItem]
    _index: int

    __slots__ = ("_name", "_id", "_items", "_index")

    def __init__(self, name: str, id: str):
        self._name = name
        self._id = id
        self._items = {}
        self._index = 0

    def __next__(self):
        items = list(self._items.items())
        if self._index == len(items) - 1:
            raise StopIteration
        self._index += 1
        return items[self._index]

    def __iter__(self):
        return self

    def check_template(self, gis: GIS) -> bool:
        """
        The `check_template` method attempts to fetch the item using its `id`, returning `True` if the type of content is an arcgis.gis.Item, `False` otherwise.  Primarily accessed by `check_template`.

        :param gis: An authenticated GIS connection.
        :type gis: arcgis.gis.GIS
        :return: Boolean indicating whether the item is of type arcgis.gis.Item.
        :rtype: bool
        """
        if type(gis.content.get(self.id)) is arcgis.gis.Item:
            return True
        else:
            return False

    def with_names(self, names: list[str]):
        """
        The *with_names* method changes the *item_name* property of the ``TemplateItem`` objects within the *items* field to match the names provided in *names*.  Fails if the number of names in *names* is not the same as the number of ``TemplateItem`` objects in *items*.

        :param names: A list of names for items in the ``Template``.
        :type names: list[str]
        :return: A modified ``Template`` with the *item_name* of each ``TemplateItem`` set to one of the names in *names*.
        :rtype: Template
        """
        if len(self._items) != len(names):
            logging.warn("Length of names must match number of items in the template.")
            logging.warn("Names: %s", len(names))
            logging.warn("Items: %s", len(self._items))
            return self
        else:
            index = 0
            tmp = Template(self._name, self._id)
            for _, value in self._items.items():
                value._item_name = names[index]
                tmp._items.update({names[index]: value})
                index += 1
        return tmp

    def read(self, layers: list[dict], searches: dict, items=[]) -> list:
        """
        The *read* method reads map layer information from the *layers* property of an arcgis.mapping.WebMap and returns a list of ``TemplateItem`` objects containing the map information.  This method is used an in internal library function, called by *Template.load* and *Template.workook_parts*.

        :param layers: List returned by the *layers* property of the target arcgis.mapping.WebMap
        :type layers: list[dict]
        :param searches: Search dictionary returned by the *get_search* method.
        :type searches: dict
        :param items: A list that holds ``TemplateItem`` objects created during the operation.
        :type items: list
        :return: A list of ``TemplateItem`` objects holding the map information from layers in the *Template*.
        :rtype: list[TemplateItem]
        """
        logging.debug("Calling read.")
        for layer in layers:
            if layer["title"] in layer:
                logging.debug("Reading layer %s.", layer["title"])
            else:
                logging.debug("Title not found.")
            if layer["layerType"] in ["GroupLayer"]:
                logging.debug("Group layer found.")
                self.read(layer["layers"], searches, items)
            if layer["layerType"] in ["ArcGISFeatureLayer"]:
                logging.debug("Feature layer found.")
                items.append(TemplateItem.from_layer(layer, self.name, searches))
            if layer["layerType"] in [
                "ArcGISMapServiceLayer",
                "ArcGISTiledMapServiceLayer",
            ]:
                logging.debug("Raster layer found.")
                items.append(TemplateItem.from_raster(layer, self.name))
        return items

    def load(self, gis: GIS):
        """
        The *load* method accesses a template web map and reads the layer data into a ``Template`` object.

        :param gis: An authenticated GIS connection.
        :type gis: arcgis.gis.GIS
        :return: A ``Template`` object containing layer data from the target web map.
        :rtype: Template
        """
        item = gis.content.get(self.id)
        searches = Template.get_search(item)
        logging.debug("Search found: %s", searches)
        wm = WebMap(item)
        data = self.read(wm.layers, searches, items=[])
        logging.debug("Layers found: %s", len(data))
        index = 0
        for datum in data:
            if datum.item_name is None:
                name = "{nm}_{id}".format(nm=self.name, id=index)
                datum._item_name = name
            self._items.update({datum.item_name: datum})
            index += 1
        return self

    @staticmethod
    def get_search(item: arcgis.gis.Item):
        """
        The *get_search* method reads the search fields from a web map and returns a dictionary with layer ids as keys and search fields as values.  An internal library function called by *Template.load* and *Template.workbook_parts*.

        :param item: An ArcGIS Item ID pointing to a non-empty web map.
        :type item: arcgis.gis.Item
        :return: A dictionary with layer IDs as keys and search fields as values, containing the searchable fields within the provided web map.
        :rtype: dict[str, list(str)]
        """
        d = {}
        map_def = item.get_data()
        if "applicationProperties" in map_def:
            map_def = map_def["applicationProperties"]
        if "viewing" in map_def:
            map_def = map_def["viewing"]
        if "search" in map_def:
            map_def = map_def["search"]
        if "layers" in map_def:
            map_def = map_def["layers"]
        for search in map_def:
            if "id" in search:
                search_id = search["id"]
                items = []
                if search_id in d:
                    items = d[search_id]
                if "field" in search:
                    search_field = search["field"]
                    if "name" in search_field:
                        items.append(search_field["name"])
                d.update({search_id: items})
        return d

    def workbook(self, path, auto=False, named=False):
        """
        The *workbook* method exports data from a ``Template`` object to a .csv workbook.  Called by *Templates.workbooks*.

        :param path: The directory or file path destination for the workbook.
        :type path: str
        :param auto: Assigns names to map layers automatically if true.
        :type bool:
        :param named: Indicates that names have been assigned to map layers using the *with_names* method, and should be preserved.
        :type named: bool
        :return: Prints a .csv workbook to the target *path* as a side effect.
        :rtype: NoneType
        """
        lyrs = self._items.values()
        logging.debug("Layers read: %s", len(lyrs))
        df = pandas.DataFrame(data={"name": []})
        title = []
        group = []
        names = []
        id = []
        layer_def = []
        popup_info = []
        url = []
        search = []
        index = 0

        group_name = self.name

        for layer in lyrs:
            logging.debug("loop %s", layer.title)
            if auto:
                if layer.item_name is not None:
                    logging.debug("Name found: %s.", layer.item_name)
                    names.append(layer.item_name)
                else:
                    logging.debug("Name not found: auto-naming.")
                    name = "{nm}_{i}".format(nm=group_name, i=index)
                    names.append(name)
            if named:
                names.append(layer.item_name)
            title.append(layer.title)
            group.append(group_name)
            id.append(layer.id)
            layer_def.append(json.dumps(layer.layer_definition))
            popup_info.append(json.dumps(layer.popup_info))
            url.append(layer.url)
            search.append(layer.search)
            index += 1

        df["title"] = title
        df["group"] = group
        if auto or named:
            logging.debug("Adding names.")
            df["name"] = names
        df["id"] = id
        df["layer_definition"] = layer_def
        df["popup_info"] = popup_info
        df["url"] = url
        df["search"] = search
        logging.debug("Length of csv: %s", len(df["popup_info"]))
        if ".csv" not in path:
            path = PurePath(path, "{}.csv".format(group_name))
        df.to_csv(path, sep=",", index=False)

    def workbook_parts(
        self,
        gis: GIS,
        names: list[str],
        title: list[str],
        group: list[str],
        id: list[uuid.UUID],
        layer_def: list[dict],
        popup_info: list[dict],
        url: list[str],
        search: list[dict],
    ):
        """
        The *workbook_parts* method is an internal library function that reads layer data from the target web map and appends the different types of map data to the appropriate list variable passed in as an argument.  Called by *Template.workbook*.

        :param gis: An authenticated GIS connection.
        :type gis: arcgis.gis.GIS
        :param names: A list holding data on layer names.
        :type names: list[str]
        :param title: A list holding the display title of each layer.
        :type title: list[str]
        :param group: A list holding the group name of each layer.
        :type group: list[str]
        :param id: A list holding the internal unique ID of each layer.
        :type id: list[UUID]
        :param layer_def: A list holding the layer definition of each layer.
        :type layer_def: list[dict]
        :param popup_info: A list holding the popup info of each layer.
        :type popup_info: list[dict]
        :param url: A list holding the url source of each layer.
        :type url: list[str]
        :param search: A list holding the search definition for each layer.
        :type search: list[dict]
        """
        item = gis.content.get(self.id)
        searches = Template.get_search(item)
        wm = WebMap(item)
        lyrs = self.read(wm.layers, searches, [])
        index = 0
        for layer in lyrs:
            if layer.item_name is not None:
                names.append(layer.item_name)
            else:
                names.append(self.name + "_" + str(index))
            title.append(layer.title)
            group.append(self.name)
            id.append(layer.id)
            layer_def.append(layer.layer_definition)
            popup_info.append(layer.popup_info)
            url.append(layer.url)
            search.append(layer.search)
            index += 1

    @staticmethod
    def from_workbook(path: str):
        """
        The *from_workbook* method loads map data from a .csv workbook at file location *path* into a ``Template`` object.

        :param path: The file path location of the workbook.
        :type path: str
        :return: A ``Template`` object containing the layer data in the workbook.
        :rtype: Template
        """
        name = Path(path).stem
        df = pandas.read_csv(path)
        names = df["name"]
        titles = df["title"]
        group = df["group"]
        ids = df["id"]
        layer_def = df["layer_definition"]
        popup_info = df["popup_info"]
        url = df["url"]
        search = df["search"]
        items = {}
        for i in range(0, len(names)):
            search_item = []
            srch = search[i]
            match type(srch).__name__:
                case "str":
                    if srch != "[]":
                        search_item.append(srch)
                    else:
                        logging.debug("Empty search field detected.")
                case _:
                    logging.debug(type(srch))
                    search_item.extend(srch.tolist())
            logging.debug("Search set to %s", srch)
            item = TemplateItem.from_parts(
                str(titles[i]),
                str(group[i]),
                str(names[i]),
                str(layer_def[i]),
                str(popup_info[i]),
                str(url[i]),
                search_item,
                uuid.UUID(str(ids[i])),
            )
            items.update({str(names[i]): item})
        tmp = Template(name, str(ids[0]))
        tmp._items = items
        return tmp

    def into_items(self):
        """
        The *into_items* method converts a ``Template`` object into an *Items* object.

        :return: An ``Items`` object containing the layer data from the ``Template``.
        :rtype: mapmakers.Items
        """
        items = []
        for item in self.items.values():
            items.append(item.into_item())
        return mapmakers.Items(items)

    @property
    def name(self):
        """
        The *name* property holds the human-readable ``Template`` name.
        """
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def id(self):
        """
        The *id* property holds the Item ID of the template web map.
        """
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

    @property
    def items(self):
        """
        The *items* property holds a dictionary with ``TemplateItem`` objects for values, and the item names of the ``TemplateItem`` objects as the keys.
        """
        return self._items


@dataclass
class Templates:
    """
    The ``Templates`` class holds references to one or more ``Template`` objects.
    """

    _template: dict[str, Template]

    __slots__ = "_template"

    def __init__(self):
        self._template = {}

    def __iter__(self):
        iter(self._template)

    def add(self, template: Template):
        """
        A wrapper around the *update* method for the dictionary in the *template* property.  The *add* method takes a *template* as an argument, and updates the *template* property to contain the *template* as a value, using the *template* name as a key.

        :param template: The target ``Template`` object to add to the ``Templates`` object.
        :type template: Template
        :return: Modifies the ``Templates`` object in place.
        :rtype: NoneType
        """
        if template.name != None:
            self._template.update({template.name: template})
        else:
            logging.warn("Template is unnamed.")

    @staticmethod
    def from_obj(templates: dict[str, str], gis: GIS):
        """
        The *from_obj* method converts template information passed in a dictionary into a ``Templates`` class object.

        :param templates: A dictionary with template names as keys and arcgis.mapping.WebMap Item IDs as values.
        :type templates: dict[str, str]
        :return: A ``Templates`` object containing layer data from the web maps at the Item IDs stored in *templates*.
        :rtype: Templates
        """
        res = Templates()
        bar = progressbar.ProgressBar(max_value=len(templates))
        index = 0
        for key, value in templates.items():
            template = Template(key, value)
            template.load(gis)
            res._template.update({key: template})
            index += 1
            bar.update(index)
        return res

    def workbooks(self, dir: str, auto=False):
        """
        For each ``Template`` in the *template* property, the *workbooks* method prints a .csv workbook to the directory at *dir* containing the layer data of the template web map.

        :param dir: The target directory path in which to print the .csv workbooks.
        :type dir: str
        :param auto: Assigns names to map layers automatically if true.
        :type auto: bool
        :return: Writes one or more .csv workbooks to target directory *dir* as a side effect.
        :rtype: NoneType
        """
        path = Path(dir)
        logging.debug("Path is {%s}", path)
        if path.is_dir():
            for key, value in self._template.items():
                workbook = PurePath(path, "{}.csv".format(key))
                logging.debug("Workbook: %s", workbook)
                value.workbook(path, auto)
        else:
            logging.warn("Dir must be a valid directory.")

    def workbook(self, gis: GIS, dir: str, auto=False):
        """
        The *workbook* method prints a .csv workbook containing layer data from all of the ``Template`` objects in the *template* property.  If *dir* points to a directory, the workbook will be placed in the directory under the name "workbook.csv".  If *dir* provides a file name ending with a ".csv" extension, the workbook will be assigned the given file name.

        :param gis: An authenticated GIS connection.
        :type gis: arcgis.gis.GIS
        :param dir: The path and (optionally) file name at which to print the .csv workbook.
        :type dir: str
        :param auto: Assigns names to map layers automatically if true.
        :type bool:
        :return: Writes a .csv workbook to the target directory *dir* as a side effect.
        :rtype: NoneType
        """
        path = Path(dir)
        logging.debug("Path is {%s}", path)
        df = pandas.DataFrame(data={"name": []})
        names = []
        title = []
        group = []
        id = []
        layer_def = []
        popup_info = []
        url = []
        search = []

        if path.is_dir():
            size = len(self._template)
            bar = progressbar.ProgressBar(max_value=size)
            index = 0
            for key, value in self._template.items():
                logging.debug("Adding template %s", key)
                value.workbook_parts(
                    gis, names, title, group, id, layer_def, popup_info, url, search
                )
                index += 1
                bar.update(index)
            logging.debug("layers found: %s", len(title))
            if auto:
                df["name"] = names

            df["title"] = title
            df["group"] = group
            df["id"] = id
            df["layer_definition"] = layer_def
            df["popup_info"] = popup_info
            df["url"] = url
            df["search"] = search
            logging.debug("Length of csv: %s", len(df["popup_info"]))
            path = PurePath(path, "workbook.csv")
            df.to_csv(path, sep=",", index=False)

        else:
            logging.warn("Dir must be a valid directory.")

    @staticmethod
    def from_workbook(path: str):
        """
        The *from_workbook* method loads the contents of the .csv workbook at *path* into a ``Templates`` object.

        :param path: The file path to the location of the .csv workbook.
        :type path: str
        :return: A ``Templates`` object containing map layer data from the workbook.
        :rtype: Templates
        """
        tmp = Template.from_workbook(path)
        t = Templates()
        for item in tmp.items.values():
            name = item.group_name
            if name not in t._template:
                temp = Template(name, str(item.id))
                if type(item.item_name) == str:
                    temp._items.update({item.item_name: item})
                t._template.update({name: temp})
            else:
                if type(item.item_name) == str:
                    t._template[name]._items.update({item.item_name: item})
        return t

    def into_items(self):
        """
        The *into_items* method converts a ``Templates`` object into an *Items* object.  Iterates through the ``Template`` objects in the *template* property and calls *Template.into_items* on each object.

        :return: An ``Items`` object containing the layer data from the ``Templates``.
        :rtype: mapmakers.Items
        """
        items = []
        for item in self.template.values():
            items.extend(item.into_items())
        return mapmakers.Items(items)

    @property
    def template(self):
        """
        The *template* property holds a dictionary containing ``Template`` objects as values and using the ``Template`` names as keys.
        """
        return self._template
