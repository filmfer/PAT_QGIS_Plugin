# -*- coding: utf-8 -*-
"""
/***************************************************************************
  CSIRO Precision Agriculture Tools (PAT) Plugin
  pat - This script initializes the plugin, making it known to QGIS.
           -------------------
        begin      : 2017-05-25
        git sha    : $Format:%H$
        copyright  : (c) 2018, Commonwealth Scientific and Industrial Research Organisation (CSIRO)
        email      : PAT@csiro.au
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the associated CSIRO Open Source Software       *
 *   License Agreement (GPLv3) provided with this plugin.                  *
 *                                                                         *
 ***************************************************************************/

"""
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()

import configparser

import os
import sys
import site
import platform
import tempfile
import osgeo.gdal
import logging
from . import resources  # import resources like icons for the plugin

from qgis.core import Qgis, QgsApplication
from qgis.gui import QgsMessageBar
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import pluginMetadata
 
PLUGIN_DIR = os.path.abspath( os.path.dirname(__file__))
PLUGIN_NAME = "PAT"
PLUGIN_SHORT= "PAT"
LOGGER_NAME = 'pyprecag'

# This matches the folder pyprecag uses.
TEMPDIR = os.path.join(tempfile.gettempdir(), 'PrecisionAg')

''' Adds the path to the external libraries to the sys.path if not already added'''
if PLUGIN_DIR not in sys.path:
    sys.path.append(PLUGIN_DIR)

# if os.path.join(PLUGIN_DIR, 'ext-libs') not in sys.path:
#     site.addsitedir(os.path.join(PLUGIN_DIR, 'ext-libs'))


def classFactory(iface):
    """Load pat_toolbar class from file pat_toolbar.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    if platform.system() != 'Windows':
        message = 'PAT is only available for Windows'

        iface.messageBar().pushMessage("ERROR", message,
                                       level=Qgis.Critical,
                                       duration=0)

        QMessageBox.critical(None, 'Error', message)
        sys.exit(message)

    if not os.path.exists(TEMPDIR):
        os.mkdir(TEMPDIR)

    from .util.settings import read_setting, write_setting
    if read_setting(PLUGIN_NAME + "/DISP_TEMP_LAYERS") is None:
        write_setting(PLUGIN_NAME + "/DISP_TEMP_LAYERS", False)

    if read_setting(PLUGIN_NAME + "/DEBUG") is None:
        write_setting(PLUGIN_NAME + "/DEBUG", False)

    try:
        from pyprecag import config
        config.set_debug_mode(read_setting(PLUGIN_NAME + "/DEBUG",bool))
    except ImportError:
        # pyprecag is not yet installed
        pass

    # the custom logging import requires qgis_config so leave it here
    from .util.custom_logging import setup_logger

    # Call the logger pyprecag so it picks up the module debugging as well.
    setup_logger(LOGGER_NAME)
    LOGGER = logging.getLogger(LOGGER_NAME)
    LOGGER.addHandler(logging.NullHandler())   # logging.StreamHandler()

    from .util.check_dependencies import (check_pat_symbols, check_R_dependency,check_gdal_dependency,
                                          check_python_dependencies)

    meta_version = pluginMetadata('pat','version')
    plugin_state = '\nPAT Plugin:\n'
    plugin_state += '    {:25}\t{}\n'.format('QGIS Version:', Qgis.QGIS_VERSION)
    plugin_state += '    {:25}\t{}\n'.format('Python Version:',  sys.version)
    plugin_state += '    {:25}\t{} {}'.format('PAT:', pluginMetadata('pat', 'version'),
                                                      pluginMetadata('pat', 'update_date'))
    LOGGER.info(plugin_state)



    # if not check_gdal:
    #     LOGGER.critical('QGIS Version {} and GDAL {} is are not currently supported.'.format(Qgis.QGIS_VERSION, gdal_ver))
    #
    #     message = ('QGIS Version {} and GDAL {}  are not currently supported. '
    #                'Downgrade QGIS to an earlier version. If required email PAT@csiro.au '
    #                'for assistance.'.format(Qgis.QGIS_VERSION, gdal_ver))
    #
    #     iface.messageBar().pushMessage("ERROR Failed Dependency Check", message,
    #                                    level= Qgis.Critical, duration=0)
    #     QMessageBox.critical(None, 'Failed Dependency Check', message)
    #     sys.exit(message)

    gdal_ver = check_gdal_dependency()
    check_pat_symbols()
    # check_R_dependency()
    result = check_python_dependencies(PLUGIN_DIR, iface)
    if len(result) > 0:
        iface.messageBar().pushMessage("ERROR Failed Dependency Check", result, level= Qgis.Critical, duration=0)
    from .pat_toolbar import pat_toolbar

    return pat_toolbar(iface)
