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

from guicontrols import AppStaticBox, ROTextCtrl

#This code is predominantly from the pyslip demo application

# tiles info
MinTileLevel = 0

# initial view level and position
InitViewLevel = 3

InitViewPosition = (250, 30)             # Central US in GMT coordinate system

LonLatPrecision = 3
DefaultAppSize = (1100, 770)

PackBorder = 0

class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=DefaultAppSize, title="IPtool v1")
        self.SetMinSize(DefaultAppSize)
        #TODO where did DefaultAppSize come form
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.SetBackgroundColour(wx.WHITE)
        self.panel.ClearBackground()

        self.tile_source = tiles.Tiles()

        self.make_gui(self.panel)

        self.init()

        self.demo_select_dispatch = {}

        self.pyslip.Bind(pyslip.EVT_PYSLIP_SELECT, self.handle_select_event)
        self.pyslip.Bind(pyslip.EVT_PYSLIP_BOXSELECT, self.handle_select_event)
        self.pyslip.Bind(pyslip.EVT_PYSLIP_POSITION, self.handle_position_event)
        self.pyslip.Bind(pyslip.EVT_PYSLIP_LEVEL, self.handle_level_change)

        self.geoIP = MaxMindIPProvider('..\\geoipdb\\GeoLite2-City_20170502\\GeoLite2-City.mmdb')

    def init(self):
        wx.CallAfter(self.final_setup, InitViewLevel, InitViewPosition)
        self.pyslip.OnSize()
        self.Centre()

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
        ipEntry = self.make_gui_IP_box(parent)
        ip.Add(ipEntry, proportion=1, flag=wx.EXPAND|wx.ALL)
        controls.Add(ip, proportion=1, flag=wx.EXPAND|wx.ALL)

        detailbox = wx.BoxSizer(wx.HORIZONTAL)
        details = self.make_gui_details(parent)
        detailbox.Add(details, proportion=1, flag=wx.EXPAND|wx.ALL)
        controls.Add(detailbox,proportion=1, flag=wx.EXPAND|wx.ALL)
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
        
    def onFind(self, event):
        #TODO make this remember previously queried IP addresses. (with some sort of cache timeout?)
        ipvalue = self.ipctrl.GetValue()
        lat, lon = self.geoIP.getLatLon(ipvalue)[0:2]
        #This conversion from real lat/lon to map lat/lon only works for Pyslip 3.0.4 "GMT" tileset. 
        if (lon < -65):
            lon += 360
        point = (lon, lat)
        textData = [(lon, lat, ipvalue, {'placement': 'sw'})]
        self.pyslip.AddTextLayer(textData, map_rel=True, 
                                        name='<text_layer>', 
                                        visible=True,
                                        delta=40,
                                        show_levels=[1,2,3,4,5,6,7],
                                        placement='w',
                                        selectable=True,
                                        radius = 2)
        self.updateDetails(ipvalue)
        self.pyslip.GotoPosition(point)     

    def updateDetails(self, ip):
        city = self.geoIP.getCity(ip)
        country = self.geoIP.getCountry(ip)        
        self.ip_details.SetLabel(ip + "\n" + str(city) + "\n" + str(country))

    def make_gui_details(self, parent):
        """ Build the ip details box """
        self.ip_details = wx.StaticText(parent, wx.ID_ANY, "IP\nCity\nCountry")
        sb = AppStaticBox(parent, "Details")
        sizer = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        sizer.Add(self.ip_details, proportion=1, border=PackBorder,
                flag=wx.EXPAND)
        return sizer

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
        selection = event.selection
        if selection:
            ip = selection[0][2]
            if ip:
                self.updateDetails(ip)

    def handle_position_event(self, event):
        """Handle a pySlip POSITION event."""

        posn_str = ''
        if event.mposn:
            (lon, lat) = event.mposn
            posn_str = ('%.*f / %.*f'
                        % (LonLatPrecision, lon, LonLatPrecision, lat))

        self.mouse_position.SetValue(posn_str)

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


if __name__ == '__main__':
    # start wxPython app
    app = wx.App()
    app_frame = AppFrame()
    app_frame.Show()

    app.MainLoop()

