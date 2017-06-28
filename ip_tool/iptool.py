from geo_ip import MaxMindIPProvider
from file_parser import FileParser
from ip_filter import IPFilter
from rdap_lookup import RDAPLookup

import sys
from multiprocessing import Pool
import json

import wx
import pyslip
import pyslip.gmt_local_tiles as tiles

def mergeDicts(x, y): #Built in way to combine two dictionaries is a python 3 feature
    z = x.copy()
    z.update(y)
    return z

def getRDAP(ip):
    rdaplookup = RDAPLookup()
    return rdaplookup.getRDAPDict(ip)

def rdapLookup(ipList):
    rdaplookup = RDAPLookup()
    results = []
    p = Pool(8)     #Using fewer workers reduces risk of connection refusal from lookup servers
    numTasks = len(ipList)
    for i, result in enumerate(p.imap_unordered(getRDAP, ipList), 1):
        try:
            sys.stderr.write('\rProgress: {0:.2%}'.format(i/float(numTasks)))
            results.append(result)
        except Exception as e:
            print e
    p.close()
    p.join()
    return results

mmIP = MaxMindIPProvider('..\\geoipdb\\GeoLite2-City_20170502\\GeoLite2-City.mmdb')
def getIP(ip):
    return mmIP.getLatLon(ip)

#Stealing straight from the demo

# tiles info
MinTileLevel = 0

# initial view level and position
InitViewLevel = 4

# this will eventually be selectable within the app
# a selection of cities, position from WikiPedia, etc
InitViewPosition = (0.0, 51.48)             # Greenwich, England

LonLatPrecision = 3
DefaultAppSize = (1100, 770)
TileSources = [
               ('BlueMarble tiles', 'pyslip.bm_tiles'),
               ('GMT tiles', 'pyslip.gmt_local_tiles'),
               ('ModestMaps tiles', 'pyslip.mm_tiles'),
               ('MapQuest tiles', 'pyslip.mq_tiles'),
               ('OpenStreetMap tiles', 'pyslip.osm_tiles'),
               ('Stamen Toner tiles', 'pyslip.stmt_tiles'),
               ('Stamen Transport tiles', 'pyslip.stmtr_tiles'),
               ('Stamen Watercolor tiles', 'pyslip.stmw_tiles'),
              ]
DefaultTileset = 'GMT tiles'
PackBorder = 0

class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=DefaultAppSize, title="IPtool v1")
        self.SetMinSize(DefaultAppSize)
        #TODO where did DefaultAppSize come form
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.SetBackgroundColour(wx.WHITE)
        self.panel.ClearBackground()

        menuBar = wx.MenuBar()
        tile_menu = wx.Menu()

        self.tile_source= None
        self.id2tiledata = {}
        self.name2guiid = {}

        self.default_tileset_name = None 


        for (name, module_name) in TileSources:
            new_id = wx.NewId()
            tile_menu.Append(new_id, name, name, wx.ITEM_RADIO)
            self.Bind(wx.EVT_MENU, self.onTilesetSelect)
            self.id2tiledata[new_id] = (name, module_name, None)
            self.name2guiid[name] = new_id
            if name == DefaultTileset:
                self.default_tileset_name = name

        if self.default_tileset_name is None:
            raise Exception('Bad Tilesources({0}'.format(str(TileSources)))

        menuBar.Append(tile_menu, "&Tileset")
        self.SetMenuBar(menuBar)

        self.tile_source = tiles.Tiles()

        self.make_gui(self.panel)

        #self.init()
        #maybe don't need this right now

        self.demo_select_dispatch = {}
        #TODO define this

        self.pyslip.Bind(pyslip.EVT_PYSLIP_SELECT, self.handle_select_event)
        self.pyslip.Bind(pyslip.EVT_PYSLIP_BOXSELECT, self.handle_select_event)
        self.pyslip.Bind(pyslip.EVT_PYSLIP_POSITION, self.handle_position_event)
        self.pyslip.Bind(pyslip.EVT_PYSLIP_LEVEL, self.handle_level_change)

        item_id = self.name2guiid[self.default_tileset_name]
        tile_menu.Check(item_id, True)

    def init(self):
        self.pyslip.OnSize()
        wx.CallAfter(self.final_setup, InitViewLevel, InitViewPosition)

    def final_setup(self, level, position):
        """Perform final setup.

        level     zoom level required
        position  position to be in centre of view

        We do this in a CallAfter() function for those operations that
        must not be done while the GUI is "fluid".
        """
        self.pyslip.GotoLevelAndPosition(level, position)

    def make_gui(self, parent):

        all_display = wx.BoxSizer(wx.HORIZONTAL)
        parent.SetSizer(all_display)

        sl_box = self.make_gui_view(parent)
        all_display.Add(sl_box, proportion=1, border=PackBorder, flag=wx.EXPAND)

        controls = self.make_gui_controls(parent)
        all_display.Add(controls, proportion = 0, border=PackBorder)

        parent.SetSizerAndFit(all_display)
        parent.Layout()

    def make_gui_view(self, parent):
        """Build the map view widget parent  reference to the widget parent Returns the static box sizer."""
        sb = AppStaticBox(parent, '', style=wx.NO_BORDER)
        self.pyslip = pyslip.PySlip(parent, tile_src=self.tile_source)

        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(self.pyslip, proportion=1, border = PackBorder, flag=wx.EXPAND)
        return box

    def make_gui_controls(self, parent):
        # all controls in vertical box sizer
        controls = wx.BoxSizer(wx.VERTICAL)

        # put level and position into one 'controls' position
        l_p = wx.BoxSizer(wx.HORIZONTAL)
        level = self.make_gui_level(parent)
        l_p.Add(level, proportion=0, flag=wx.EXPAND|wx.ALL)
        mouse = self.make_gui_mouse(parent)
        l_p.Add(mouse, proportion=0, flag=wx.EXPAND|wx.ALL)
        controls.Add(l_p, proportion=0, flag=wx.EXPAND|wx.ALL)


        ip = wx.BoxSizer(wx.HORIZONTAL)
        level = self.make_gui_IP_box(parent)
        ip.Add(level, proportion=0, flag=wx.EXPAND|wx.ALL)
        controls.Add(ip, proportion=0, flag=wx.EXPAND|wx.ALL)
        return controls

    def make_gui_level(self, parent):
        """Build the control that shows the level.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create objects
        txt = wx.StaticText(parent, wx.ID_ANY, 'Level: ')
        self.map_level = ROTextCtrl(parent, '', size=(30,-1),
                                    tooltip='Shows map zoom level')

        # lay out the controls
        sb = AppStaticBox(parent, 'Map level')
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(txt, border=PackBorder, flag=(wx.ALIGN_CENTER_VERTICAL
                                              |wx.ALIGN_RIGHT|wx.LEFT))
        box.Add(self.map_level, proportion=0, border=PackBorder,
                flag=wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

        return box

    def make_gui_IP_box(self, parent):
        label = wx.StaticText(parent, wx.ID_ANY, 'IP: ')
        self.ipctrl = wx.TextCtrl(parent, wx.ID_ANY, value='ip')
        self.findbtn = wx.Button(parent, label = "Find")
        self.findbtn.Bind(wx.EVT_BUTTON, self.onFind)
        sb = AppStaticBox(parent, "IP Locate")
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(label, border=PackBorder, flag=(wx.ALIGN_CENTER_VERTICAL
                                              |wx.ALIGN_RIGHT|wx.LEFT))
        box.Add(self.ipctrl, flag=(wx.ALIGN_CENTER_VERTICAL
                            |wx.ALIGN_CENTER|wx.CENTER))
        box.Add(self.findbtn, proportion=0, border=PackBorder,
                flag=(wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL))
        return box
        
    def onFind(self, somethin):
        ipvalue = self.ipctrl.GetValue()
        lat, lon = getIP(ipvalue)[0:2]
        #TODO we need to do tileset dependent conversion to the geo coordinate system used by that tileset. 
        # in the case of geo tiles, anything lower than -65 
        if (lon < -65):
            lon += 360
        point = (lon, lat)
        print point
        self.pyslip.AddPointLayer([point,], map_rel=True, visible=True, show_levels=None, 
        selectable=False, name='<ip point: {0}'.format(ipvalue), radius=4, colour='blue', size = DefaultAppSize)
        #TODO refactor

    def make_gui_mouse(self, parent):
        """Build the mouse part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create objects
        txt = wx.StaticText(parent, wx.ID_ANY, 'Lon/Lat: ')
        self.mouse_position = ROTextCtrl(parent, '', size=(120,-1),
                                         tooltip=('Shows the mouse '
                                                  'longitude and latitude '
                                                  'on the map'))

        # lay out the controls
        sb = AppStaticBox(parent, 'Mouse position')
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(txt, border=PackBorder, flag=(wx.ALIGN_CENTER_VERTICAL
                                     |wx.ALIGN_RIGHT|wx.LEFT))
        #box.Add(self.mouse_position, proportion=1, border=PackBorder,
        box.Add(self.mouse_position, proportion=0, border=PackBorder,
                flag=wx.RIGHT|wx.TOP|wx.BOTTOM)

        return box

    def handle_select_event(self, event):
        """Handle a pySlip point/box SELECT event."""
        layer_id = event.layer_id
        self.demo_select_dispatch.get(layer_id, self.null_handler)(event)

    def handle_position_event(self, event):
        """Handle a pySlip POSITION event."""

        posn_str = ''
        if event.mposn:
            (lon, lat) = event.mposn
            posn_str = ('%.*f / %.*f'
                        % (LonLatPrecision, lon, LonLatPrecision, lat))

        self.mouse_position.SetValue(posn_str)

    def onTilesetSelect(self, event):
        """User selected a tileset from the menu.

        event  the menu select event
        """

        menu_id = event.GetId()
        try:
            (name, module_name, new_tile_obj) = self.id2tiledata[menu_id]
        except KeyError:
            # badly formed self.id2tiledata element
            raise Exception('self.id2tiledata is badly formed:\n%s'
                            % str(self.id2tiledata))

        if new_tile_obj is None:
            # haven't seen this tileset before, import and instantiate
            module_name = self.id2tiledata[menu_id][1]
            exec 'import %s as tiles' % module_name
            new_tile_obj = tiles.Tiles()

            # update the self.id2tiledata element
            self.id2tiledata[menu_id] = (name, module_name, new_tile_obj)

        self.pyslip.ChangeTileset(new_tile_obj)

    def handle_level_change(self, event):
        """Handle a pySlip LEVEL event."""

        self.map_level.SetValue('%d' % event.level)

    ######
    # Handle adding/removing select handler functions.
    ######

    def add_select_handler(self, id, handler):
        """Add handler for select in layer 'id'."""

        self.demo_select_dispatch[id] = handler

    def del_select_handler(self, id):
        """Remove handler for select in layer 'id'."""

        del self.demo_select_dispatch[id]

class AppStaticBox(wx.StaticBox):

    def __init__(self, parent, label, *args, **kwargs):
#        if label:
#            label = '  ' + label + '  '
        if 'style' not in kwargs:
            kwargs['style'] = wx.NO_BORDER
        wx.StaticBox.__init__(self, parent, wx.ID_ANY, label, *args, **kwargs)

# background colour for the 'read-only' text field
ControlReadonlyColour = '#ffffcc'

class ROTextCtrl(wx.TextCtrl):
    """Override the wx.TextCtrl widget to get read-only text control which
    has a distinctive background colour."""

    def __init__(self, parent, value, tooltip='', *args, **kwargs):
        wx.TextCtrl.__init__(self, parent, wx.ID_ANY, value=value,
                             style=wx.TE_READONLY, *args, **kwargs)
        self.SetBackgroundColour(ControlReadonlyColour)
        self.SetToolTip(wx.ToolTip(tooltip))
        
if __name__ == '__main__':
    # start wxPython app
    app = wx.App()
    app_frame = AppFrame()
    app_frame.Show()

    app.MainLoop()

