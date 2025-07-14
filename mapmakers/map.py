from dataclasses import dataclass
from mapmakers.template import Template, TemplateItem
from mapmakers.utils import create_layer_id
import arcgis
from arcgis.gis import GIS
from arcgis.mapping import WebMap
import json
import logging
import random
import requests


@dataclass
class Item:
    """
    The ``Item`` class holds a template reference and configuration information for a map layer.
    """

    _url: str
    _template: TemplateItem | None
    _visible: bool
    _title: str | None
    _opacity: float | None

    __slots__ = (
        "_url",
        "_template",
        "_visible",
        "_title",
        "_opacity",
    )

    def __init__(
        self, url: str, template=None, visible=False, title=None, opacity=None
    ):
        """
        Creates a new map Item from a given URL and optional TemplateItem, setting the visibility, title and opacity using the `visible`, `title` and `opacity` fields respectively.

        :param url: A string representation of the ArcGIS service URL.
        :type url: str
        :param template: The ``TemplateItem`` to associate with the service URL.
        :type template: TemplateItem
        :param visible: Bool setting the default visibility of the map layer.
        :type visible: bool
        :param title: Sets the title of the map layer using a string.
        :type title: str
        :param opacity: Sets the opacity of the map layer.
        :type opacity: float
        :return: Returns the newly created map Item.
        :rtype: Item
        """
        self._url = url
        self._template = template
        self._visible = visible
        self._title = title
        self._opacity = opacity

    @staticmethod
    def check_url_in(path: str) -> bool:
        """
        The `check_url_in` static method sends a "GET" request to `path`, returning `True` if the status code is 200 and `False` otherwise.  Primarily used by calling `check_url`.

        :param path: String representation of the target URL.
        :type path: str
        :return: Boolean indicating whether a "GET" request returns a status code 200.
        :rtype: bool
        """
        check = requests.get(path)
        if check.status_code == 200:
            logging.info("Url %s is valid.", path)
            return True
        else:
            logging.warn("Url %s not found.", path)
            return False

    def check_url(self) -> bool:
        """
        The `check_url` method wraps the static method `check_url_in` to enable ergonomic checking of ``Item`` urls.

        :return: Boolean indicating whether a "GET" request returns a status code 200.
        :rtype: bool
        """
        return Item.check_url_in(self._url)

    def layer(self):
        """
        The *layer* method converts feature class data in a map ``Item`` into a map ``Layer``.

        :return: ``Layer`` instance constructed from self.
        :rtype: Layer
        """
        return Layer(self)

    def group(self, name: str, visible: bool = True):
        """
        The *group* method converts a map ``Item`` into a map ``Group`` with name *name*.

        :param name: Display name of the ``Group`` layer.
        :type name: str
        :return: ``Group`` instance constructed from self.
        :rtype: Group
        """
        return Group.from_item(name, self, visible)

    def raster(self):
        """
        The *raster* method converts raster data in a map ``Item`` into a map ``Layer``.

        :return: ``Layer`` instance constructed from self.
        :rtype: Layer
        """
        return Layer.from_raster(self)

    def vector_tile(self):
        return Layer.from_vector_tile(self)

    @property
    def url(self):
        """
        The *url* property is a text representation of the URL for an ArcGIS service.
        """
        return self._url

    @url.setter
    def url(self, path):
        self._url = path

    @property
    def template(self):
        """
        The *template* property is a ``TemplateItem`` associated with an ``Item``.
        """
        return self._template

    @template.setter
    def template(self, value: TemplateItem):
        self._template = value

    @property
    def visible(self):
        """
        The *visible* property sets the default visibility of the map ``Item``.
        """
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        self._visible = value

    @property
    def title(self):
        """
        The *title* property sets the display title of the map ``Item``.
        """
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    @property
    def opacity(self):
        """
        The *opacity* field sets the opacity of the map ``Item``.
        """
        return self._opacity

    @opacity.setter
    def opacity(self, value: float):
        self._opacity = value


@dataclass
class Items:
    """
    The ``Items`` class holds a list of ``Item`` objects.
    """

    _items: list[Item]
    _index: int

    __slots__ = ("_items", "_index")

    def __init__(self, items: list[Item]):
        self._items = items
        self._index = -1

    def __next__(self):
        if self._index == len(self._items) - 1:
            raise StopIteration
        self._index += 1
        return self._items[self._index]

    def __iter__(self):
        return self

    def reverse(self):
        """Wrapper calling reverse on the _items field of `Items`."""
        self._items.reverse()
        return self

    # def gen(self):
    #     for index in range(0, len(self._items), 1):
    #         yield self._items[index]

    @staticmethod
    def from_names(urls: list[str], names: list[str], template: Template):
        """
        The *from_names* method creates an ``Items`` instance from a list of urls *urls* and a list of names *names*.  Iterates through the urls in *urls* and names in *names*, assigning each to the next layer in the template *template*.  The number of urls and names must match the number of layers in the template.

        :param urls: A list of urls for the target sources of each layer.
        :type urls: list[str]
        :param names: A list of names for each map layer.
        :type names: list[str]
        :param template: A ``Template`` object created from a template web map.
        :type template: mapmakers.template.Template
        :return: An ``Items`` object with *urls* and *names* mapped to layers in *template*.
        :rtype: Items
        """
        if len(urls) != len(names):
            logging.warn("The number of urls and names must be equal.")
            return
        else:
            items = []
            for i in range(0, len(urls)):
                items.append(Item(urls[i], template._items[names[i]]))
            return Items(items)

    @staticmethod
    def from_template(urls: list[str], template: Template):
        """
        The *from_template* method creates an ``Items`` object from a list of urls *urls* and a web map *template*.  The number of urls and template items must be equal.

        :param urls: A list of url target sources for the map layers in the template.
        :type urls: list[str]
        :param template: A ``Template`` object containing layer data for the web map.
        :type template: mapmakers.template.Template
        :return: An ``Items`` object with *urls* mapped to layers in *template*.
        :rtype: Items
        """
        if len(urls) != len(template.items):
            logging.warn("The number of urls and template items must be equal.")
            return
        else:
            members = []
            i = 0
            items = template.items.values()
            for value in items:
                members.append(Item(urls[i], value))
                i += 1
            return Items(members)

    def group(self, name: str, visible: bool = True):
        """
        The *group* method coverts an ``Items`` object into a map ``Group`` with name *name*.

        :param name: Display name of the ``Group`` layer.
        :type name: str
        :return: ``Group`` instance constructed from self.
        :rtype: Group
        """
        return Group.from_items(name, self, visible)

    def layers(self):
        """
        The *layers* method converts the *items* in self into a ``Layers`` object.

        :return: ``Layers`` instance constructed from self.
        :rtype: Layers
        """
        return Layers.from_items(self)

    def rasters(self):
        """
        The *rasters* method converts the *items* in self into a ``Layers`` object.

        :return: ``Layers`` instance constructed from self.
        :rtype: Layers
        """
        return Layers.from_rasters(self)

    def vector_tiles(self):
        return Layers.from_vector_tiles(self)

    def append(self, item: Item):
        """
        The *append* method appends the ``Item`` *item* to the list of ``Item`` objects in the property *items*. Wraps the *append* method for a list.

        :param item: An ``Item`` object to append to the list of *items* in self.
        :type item: Item
        :return: Modifies and returns self.
        :rtype: Items
        """
        self._items.append(item)
        return self

    def extend(self, items: list[Item]):
        """
        The *extend* method appends the ``Item`` objects in *items* to the *items* property of self. Wraps the *extend* method for a list.

        :param items: A list of ``Item`` objects.
        :type items: list[Item]
        :return: Modifies and returns self.
        :rtype: Items
        """
        self._items.extend(items)
        return self

    def insert(self, idx: int, item: Item):
        """
        The *insert* method inserts the ``Item`` object in *item* to the *items* property of self. Wraps the *insert* method for a list.

        :param items: A list of ``Item`` objects.
        :type item: Item
        :return: Modifies and returns self.
        :rtype: Items
        """
        self._items.insert(idx, item)
        return self

    @property
    def items(self):
        """
        The *items* property holds a list of ``Item`` objects.
        """
        return self._items

    @items.setter
    def items(self, members: list[Item]):
        self._items = members


@dataclass
class Layer:
    """
    The ``Layer`` class holds map information formatted in the JSON specification for an ESRI web map.
    """

    _layer: dict
    _search: list | None
    _index: int

    __slots__ = ("_layer", "_search", "_index")

    def __init__(self, item: Item, raster=False):
        logging.debug("Calling init for Layer.")
        contents = {}
        id = create_layer_id(random.randint(10000, 99999))
        contents.update({"id": id})
        contents.update({"url": item.url})
        if item.title is None:
            if item.template is None:
                logging.debug("Title is missing.")
            else:
                contents.update({"title": item.template.title})
        else:
            contents.update({"title": item.title})
        contents.update({"layerType": "ArcGISFeatureLayer"})
        if item.opacity is None:
            contents.update({"opacity": 0.5})
        else:
            contents.update({"opacity": item.opacity})
        if item.template is not None:
            if item.template.layer_definition is not None:
                layer_def = item.template.layer_definition
                logging.debug("Layer def type: %s", type(layer_def))
                match type(layer_def).__name__:
                    case "float":
                        layer_def = None
                    case "str":
                        if layer_def is not None:
                            if not raster:
                                logging.debug("Def: %s", layer_def)
                                if "'" in layer_def:
                                    contents.update(
                                        {"layerDefinition": eval(layer_def)}
                                    )
                                else:
                                    contents.update(
                                        {"layerDefinition": json.loads(layer_def)}
                                    )
                            else:
                                contents.update(
                                    {"layerDefinition": json.dumps(layer_def)}
                                )
                    case "dict":
                        contents.update({"layerDefinition": layer_def})
            if item.template.popup_info is not None:
                popup = item.template.popup_info
                logging.debug("Popup type: %s", type(popup))
                match type(popup).__name__:
                    case "float":
                        popup = None
                    case "str":
                        if popup is not None:
                            logging.debug("Popup: %s", popup)
                            if "'" in popup:
                                contents.update({"popupInfo": eval(popup)})
                            else:
                                contents.update({"popupInfo": json.loads(popup)})
                    case "dict":
                        contents.update({"popupInfo": popup})
            else:
                logging.debug("Popup info is 'nan'.")
        contents.update({"visibility": item.visible})
        # contents.update({"disablePopup": False})
        self._layer = contents
        self._search = None
        if item.template is not None:
            srch = item.template.search
            if srch is not None:
                if len(srch) > 0:
                    self._search = item.template.into_search(id)
        self._index = -1

    def __next__(self):
        contents = list(self._layer.items())
        if self._index == len(contents) - 1:
            raise StopIteration
        self._index += 1
        return contents[self._index]

    def __iter__(self):
        return self

    @staticmethod
    def from_raster(raster: Item):
        """
        The *from_raster* method converts the input *raster* from an ``Item`` object to a ``Layer`` object.

        :param raster: The raster ``Item`` to convert.
        :type raster: Item
        :return:  A ``Layer`` object created from *raster*.
        :rtype: Layer
        """
        logging.debug("Calling from_raster on %s.", raster.title)
        layer = Layer(raster, True)
        search = []
        data = {}
        if raster.template is not None:
            logging.debug("Template found.")
            data.update({"id": raster.template.item_name})
            if raster.template.layer_definition is not None:
                logging.debug(
                    "Layer definition found: %s", raster.template.layer_definition
                )
                layer_def = json.dumps(raster.template.layer_definition)
                logging.debug("Type of layer_def: %s", type(layer_def))
                if "ArcGISMapServiceLayer" in layer_def:
                    logging.debug("Map layer.")
                    data.update({"layerType": "ArcGISMapServiceLayer"})
                if "ArcGISTiledMapServiceLayer" in layer_def:
                    logging.debug("Tiled map layer.")
                    data.update({"layerType": "ArcGISTiledMapServiceLayer"})
            if raster.template.search is not None:
                search = raster.template.search
        data.update({"maxScale": "None"})
        data.update({"minScale": "None"})
        data.update({"opacity": 1})
        data.update({"title": raster.title})
        data.update({"url": raster.url})
        data.update({"visibility": raster.visible})
        layer.layer = data
        layer.search = search
        return layer

    @staticmethod
    def from_vector_tile(tile: Item):
        logging.debug("Calling from_vector_tile on %s", tile.title)
        layer = Layer(tile, True)
        search = []
        data = {}
        if tile.template is not None:
            logging.debug("Template found for %s", tile.title)
            data.update({"id": tile.template.item_name})
            if tile.template.layer_definition is not None:
                logging.debug(
                    "layer definition found: %s", tile.template.layer_definition
                )
                layer_def = json.dumps(tile.template.layer_definition)
                logging.debug("Type of layer_def: %s", type(layer_def))
                if "VectorTileLayer" in layer_def:
                    logging.debug("Vector tile layer.")
                    data.update({"layerType": "VectorTileLayer"})
            if tile.template.search is not None:
                search = tile.template.search
        data.update({"layerType": "VectorTileLayer"})
        data.update({"opacity": 0.5})
        data.update({"title": tile.title})
        data.update({"styleUrl": tile.url})
        data.update({"visibility": tile.visible})
        layer.layer = data
        layer.search = search
        return layer

    @staticmethod
    def from_group(group):
        """
        The *from_group* method converts a ``Group`` object into a ``Layer`` object.  Convert a ``Group`` object into a ``Layer`` object to nest one group inside another.

        :param group: The ``Group`` object to be converted to a ``Layer``.
        :type group: Group
        :return: A ``Layer`` object containing *group*.
        :rtype: Layer
        """
        layer = Layer(Item("placeholder"))
        layer.layer = group.layers
        if layer.search is None:
            layer.search = group.search
        else:
            layer.search.extend(group.search)
        return layer

    def group(self, name: str):
        """
        The *group* method converts a ``Layer`` object into a ``Group`` object.

        :param name: The display name of the ``Group``.
        :type name: str
        :return: A ``Group`` object constructed from self.
        :rtype: Group
        """
        return Group.from_layer(name, self)

    @property
    def layer(self):
        """
        The *layer* property holds a dictionary with the JSON representation for an ESRI web map.
        """
        return self._layer

    @layer.setter
    def layer(self, items: dict):
        self._layer = items

    @property
    def search(self):
        """
        The *search* property holds a dictionary with search instructions for the ``Layer`` object.
        """
        return self._search

    @search.setter
    def search(self, items: list):
        self._search = items


@dataclass
class Layers:
    """
    The ``Layers`` class holds layer data *layers* and search information *search* for multiple layers of a map.
    """

    _layers: list[dict]
    _search: list[dict]
    _index: int

    __slots__ = ("_layers", "_search", "_index")

    def __init__(self, contents: list, search: list):
        logging.debug("Calling init for Layers.")
        items = []
        for content in contents:
            match type(content).__name__:
                case "Layer":
                    items.append(content._layer)
                case "Group":
                    items.append(content._layers)
                case "dict":
                    items.append(content)
                case _:
                    logging.warn("Unexpected type: %s", type(content))
        self._layers = items
        self._search = search
        self._index = -1

    def __next__(self):
        if self._index == len(self._layers) - 1:
            raise StopIteration
        self._index += 1
        return self._layers[self._index]

    def __iter__(self):
        return self

    @staticmethod
    def from_items(items: Items):
        """
        The *from_items* method converts an ``Items`` object *items* into a ``Layers`` object.

        :param items: The ``Items`` object to convert to a ``Layers`` object.
        :type items: Items
        :return: A ``Layers`` object constructed from *items*.
        :rtype: Layers
        """
        layers = []
        search = []
        for item in items.items:
            layer = Layer(item)
            layers.append(layer.layer)
            if layer.search is not None:
                search.extend(layer.search)
        return Layers(layers, search)

    @staticmethod
    def from_group(group):
        """
        The *from_group* method converts a ``Group`` object *group* to a ``Layers`` object.

        :param group: The ``Group`` object to convert into ``Layers``.
        :type group: Group
        :return: A ``Layers`` object constructed from *group*.
        :rtype: Layers
        """
        layer = Layer(Item("placeholder"))
        layer.layer = group.group
        return Layers([layer], group.search)

    @staticmethod
    def from_rasters(rasters: Items):
        """
        The *from_rasters* method converts an ``Items`` object containing raster data *rasters* into a ``Layers`` object.

        :param rasters: The raster data to convert into ``Layers``.
        :type rasters: Items
        :return: A ``Layers`` object containing the *rasters* map information.
        :rtype: Layers
        """
        layers = []
        search = []
        for raster in rasters.items:
            layers.append(Layer.from_raster(raster))
            if raster.template is not None:
                tmp = raster.template
                if tmp.search is not None:
                    search.extend(tmp.search)
        return Layers(layers, search)

    @staticmethod
    def from_vector_tiles(tiles: Items):
        layers = []
        search = []
        for tile in tiles.items:
            layers.append(Layer.from_vector_tile(tile))
            if tile.template is not None:
                tmp = tile.template
                if tmp.search is not None:
                    search.extend(tmp.search)
        return Layers(layers, search)

    def group(self, name: str, visible: bool = True):
        """
        The *group* method converts a ``Layers`` object into a ``Group`` object.

        :param name: The display name of the ``Group`` object.
        :type name: str
        :return: A ``Group`` object constructed from self.
        :rtype: Group
        """
        return Group.from_layers(name, self, visible)

    def append(self, item):
        """
        The *append* method adds a layer to the *layers* property and any search information for the layer to the *search* property.

        :param item: The layer data to add to self.
        :type item: Layer | Layers | Group | dict | list
        :return: Modifies and returns self.
        :rtype: Layers
        """
        logging.debug("Calling append.")
        logging.debug("Type is %s", type(item))
        match type(item).__name__:
            case "Layer":
                logging.debug("Layer type.")
                self.layers.append(item.layer)
                self.search.extend(item.search)
            case "Layers":
                logging.debug("Layers type.")
                self.layers.extend(item.layers)
                self.search.extend(item.search)
            case "Group":
                logging.debug("Group type.")
                self.layers.append(item.group)
                self.search.extend(item.search)
            case "dict":
                logging.debug("Dict type.")
                self.layers.append(item)
            case "list":
                logging.debug("List type.")
                itm = item[0]
                match type(itm).__name__:
                    case "Layer":
                        logging.debug("Layer type.")
                        self.layers.append(itm.layer)
                        self.search.extend(itm.search)
                    case "Layer":
                        logging.debug("Layers type.")
                        self.layers.extend(itm.layers)
                        self.search.extend(itm.search)
                    case "Group":
                        logging.debug("Group type.")
                        self.layers.append(itm.group)
                        self.search.extend(itm.search)
                    case "dict":
                        logging.debug("Dict type.")
                        self.layers.append(itm)
            case _:
                logging.warn(
                    "Expected Layer, Layers, Group or dict.  Found %s", type(item)
                )
        return self

    def extend(self, items: list):
        """
        The *extend* method adds the layer and search data from *items* to self.  Wraps *Layers.append*.

        :param items: A list of layers to add to self.
        :type items: list[Layer | Layers | Group | dict]
        :return: Modifies and returns self.
        :rtype: Layers
        """
        logging.debug("Calling extend.")
        for item in items:
            self.append(item)
        return self

    def insert(self, idx: int, item):
        """
        The *append* method adds a layer to the *layers* property and any search information for the layer to the *search* property.

        :param item: The layer data to add to self.
        :type item: Layer | Layers | Group | dict | list
        :return: Modifies and returns self.
        :rtype: Layers
        """
        logging.debug("Calling append.")
        logging.debug("Type is %s", type(item))
        match type(item).__name__:
            case "Layer":
                logging.debug("Layer type.")
                self.layers.insert(idx, item.layer)
                self.search.extend(item.search)
            case "Layers":
                logging.debug("Layers type.")
                self.layers.insert(idx, item.layers)
                self.search.extend(item.search)
            case "Group":
                logging.debug("Group type.")
                self.layers.insert(idx, item.group)
                self.search.extend(item.search)
            case "dict":
                logging.debug("Dict type.")
                self.layers.insert(idx, item)
            case "list":
                logging.debug("List type.")
                itm = item[0]
                match type(itm).__name__:
                    case "Layer":
                        logging.debug("Layer type.")
                        self.layers.insert(idx, itm.layer)
                        self.search.extend(itm.search)
                    case "Layer":
                        logging.debug("Layers type.")
                        self.layers.insert(idx, itm.layers)
                        self.search.extend(itm.search)
                    case "Group":
                        logging.debug("Group type.")
                        self.layers.insert(idx, itm.group)
                        self.search.extend(itm.search)
                    case "dict":
                        logging.debug("Dict type.")
                        self.layers.insert(idx, itm)
            case _:
                logging.warn(
                    "Expected Layer, Layers, Group or dict.  Found %s", type(item)
                )
        return self

    @property
    def layers(self):
        """
        The *layers* property holds a list of dictionaries with the JSON representation of each layer in ``Layers``.
        """
        return self._layers

    @layers.setter
    def layers(self, items: list[dict]):
        self._layers = items

    @property
    def search(self):
        """
        The *search* property holds a list of dictionaries with the JSON representation of the search fields for each layer in ``Layers``.
        """
        return self._search

    @search.setter
    def search(self, items: list):
        self._search = items


@dataclass
class Group:
    """
    The ``Group`` class holds the JSON representation of a web map group layer and its search fields.
    """

    _group: dict
    _search: list
    _visible: bool
    _index: int

    __slots__ = ("_group", "_search", "_visible", "_index")

    def __init__(self, name: str, layers: list, search: list, visible: bool = True):
        logging.debug("Calling init for Group.")
        group = {}
        group.update({"id": create_layer_id(random.randint(10000, 99999))})
        group.update({"layerType": "GroupLayer"})
        group.update({"title": name})
        group.update({"visibility": visible})
        group.update({"layers": layers})
        self._group = group
        self._search = search
        self._index = -1

    def __next__(self):
        layers = list(self._group.items())
        if self._index == len(layers) - 1:
            raise StopIteration
        self._index += 1
        return layers[self._index]

    def __iter__(self):
        return self

    @staticmethod
    def from_items(name: str, items: Items, visible: bool = True):
        """
        The *from_items* method converts an ``Items`` object *items* into a ``Group`` object.

        :param name: The display title of the ``Group`` object.
        :type name: str
        :param items: The ``Items`` object to convert into a ``Group`` object.
        :type items: Items
        :param visible: A boolean indicating whether the group should be visible.
        :type visible: Bool
        :return: A ``Group`` object constructed from *items*.
        :rtype: Group
        """
        layers = []
        search = []
        for item in items.items:
            layer = Layer(item)
            layers.append(layer.layer)
            if layer.search is not None:
                search.extend(layer.search)
        return Group(name, layers, search, visible)

    @staticmethod
    def from_item(name: str, item: Item, visible: bool = True):
        """
        The *from_item* method converts an ``Item`` object *item* into a ``Group`` object.

        :param name: The display title of the ``Group`` object.
        :type name: str
        :param item: The ``Item`` object to convert into a ``Group`` object.
        :type item: Item
        :param visible: A boolean indicating whether the group should be visible.
        :type visible: Bool
        :return: A ``Group`` object constructed from *item*.
        :rtype: Group
        """
        return Group.from_items(name, Items([item]), visible)

    @staticmethod
    def from_layer(name: str, layer: Layer, visible: bool = True):
        """
        The *from_layer* method converts a ``Layer`` object *layer* into a ``Group`` object.

        :param layer: The ``Layer`` object to convert into a ``Group`` object.
        :type item: Layer
        :param visible: A boolean indicating whether the group should be visible.
        :type visible: Bool
        :return: A ``Group`` object constructed from *layer*.
        :rtype: Group
        """
        lyr = list(layer.layer.items())
        search = []
        if layer.search is not None:
            search = layer.search
        return Group(name, lyr, search, visible)

    @staticmethod
    def from_layers(name: str, layers: Layers, visible: bool = True):
        """
        The *from_layers* method converts a ``Layers`` object *layers* into a ``Group`` object.

        :param layers: The ``Layers`` object to convert into a ``Group`` object.
        :type item: Layers
        :param visible: A boolean indicating whether the group should be visible.
        :type visible: Bool
        :return: A ``Group`` object constructed from *layers*.
        :rtype: Group
        """
        search = []
        if layers.search is not None:
            search = layers.search
        return Group(name, layers.layers, search, visible)

    def into_layer(self):
        """
        The *into_layer* method converts the ``Group`` object into a ``Layers`` object.

        :return: A ``Layers`` object constructed from self.
        :rtype: Layers
        """
        return Layers.from_group(self)

    @property
    def group(self):
        """
        The *group* property holds the JSON representation of a web map group layer.
        """
        return self._group

    @group.setter
    def group(self, items: dict):
        self._group = items

    @property
    def search(self):
        """
        The *search* property holds the JSON representation of the search fields for the group layer.
        """
        return self._search

    @search.setter
    def search(self, items: list):
        self._search = items


@dataclass
class Map:
    """
    The ``Map`` class holds layer information and methods for building an ESRI web map.
    """

    _handle: arcgis.gis.Item
    _layers: list
    _search: list

    __slots__ = ("_handle", "_layers", "_search")

    def __init__(self, id: str, layers, gis: GIS):
        logging.debug("Calling init for Map.")
        handle = gis.content.get(id)
        lyrs = []
        search = []
        logging.debug(type(layers).__name__)
        match type(layers).__name__:
            case "Layers":
                lyrs.extend(layers.layers)
                if layers.search is not None:
                    search.extend(layers.search)
            case "Group":
                lyrs.append(layers.group)
                if layers.search is not None:
                    search.extend(layers.search)
            case "Layer":
                lyrs.append(layers.layer)
                if layers.search is not None:
                    search.extend(layers.search)
            case "Items":
                l = layers.layers()
                lyrs.extend(l.layers)
                if l.search is not None:
                    search.extend(l.search)
            case "Item":
                l = layers.layer()
                lyrs.append(l.layer)
                if l.search is not None:
                    search.extend(l.search)
            case "dict":
                lyrs.append(layers)
            case "list":
                for layer in layers:
                    match type(layer).__name__:
                        case "Layers":
                            lyrs.extend(layer.layers)
                            if layer.search is not None:
                                search.extend(layer.search)
                        case "Group":
                            lyrs.append(layer.group)
                            if layer.search is not None:
                                search.extend(layer.search)
                        case "Layer":
                            lyrs.append(layer.layer)
                            if layer.search is not None:
                                search.extend(layer.search)
                        case "Items":
                            l = layer.layers()
                            lyrs.extend(l.layers)
                            if l.search is not None:
                                search.extend(l.search)
                        case "dict":
                            lyrs.append(layer)
                        case _:
                            logging.warn("Improperly nested type.")
            case _:
                logging.warn(
                    "Expected Group, Layer or dict types.  Found type %s",
                    type(layers),
                )

        self._handle = handle
        self._layers = lyrs
        self._search = search

    def clear(self):
        """
        Remove all layers from web map.

        :return: Removes layers from web map at `handle` as side effect.
        :rtype: NoneType
        """
        definition = self._handle.get_data()
        if "applicationProperties" in definition:
            if "viewing" in definition["applicationProperties"]:
                logging.debug("Stripping search terms.")
                definition["applicationProperties"]["viewing"].pop("search")
            else:
                logging.debug("viewing not found.")
        else:
            logging.debug("application properties not found.")
        webmap = WebMap(self._handle)
        if webmap.layers is None:
            logging.debug("No layers found to clear.")
            return
        layers = webmap.layers
        for layer in layers:
            webmap.remove_layer(layer)
        webmap.update()

        # Check to see if layers remain, call recursively if so
        if len(webmap.layers) != 0:
            self.clear()
        logging.debug("Layers cleared.")

    def build(self):
        """
        The *build* method attempts to clear and update the target web map in the *handle* property with the layer information in the *layers* property and the search information in the *search* property.

        :return: Modifies the target web map as a side effect.
        :rtype: NoneType
        """
        self.clear()
        definition = self._handle.get_data()
        if "operationalLayers" not in definition:
            logging.debug("Adding operational layers.")
            definition.update({"operationalLayers": [json.loads(str(self._layers))]})
        else:
            logging.debug("Appending to operational layers.")
            definition["operationalLayers"].extend(self._layers)
        if self._search is not None:
            if len(self._search) > 0:
                logging.debug("Adding search.")
                logging.debug(self._search)
                search = {}
                search.update({"enabled": True})
                search.update({"disablePlaceFinder": False})
                search.update({"hintText": "Address or Fields"})
                search.update({"layers": self._search})
                if "applicationProperties" in definition:
                    if "viewing" in definition["applicationProperties"]:
                        definition["applicationProperties"]["viewing"].update(
                            {"search": search}
                        )
                    else:
                        logging.debug("viewing not found.")
                        definition["applicationProperties"].update(
                            {"viewing": {"search": search}}
                        )
                else:
                    logging.debug("application properties not found.")
                    definition.update(
                        {"applicationProperties": {"viewing": {"search": search}}}
                    )
            else:
                logging.debug("Search field empty.")
        self._handle.update({"text": str(definition)})

    @property
    def handle(self):
        """
        The *handle* property holds the ESRI Item ID of the target web map.
        """
        return self._handle

    @handle.setter
    def handle(self, item: arcgis.gis.Item):
        self._handle = item

    @property
    def layers(self):
        """
        The *layers* property holds the layer information associated with the web map.
        """
        return self._layers

    @layers.setter
    def layers(self, items: list):
        self._layers = items

    @property
    def search(self):
        """
        The *search* property holds the search information associated with the web map.
        """
        return self._search

    @search.setter
    def search(self, items: list):
        self._search = items
