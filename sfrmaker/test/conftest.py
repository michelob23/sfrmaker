import os
import copy
import platform
import flopy
import flopy.modflow as fm
import pandas as pd
import pytest
import sfrmaker


@pytest.fixture(scope="session")
def project_root_path():
    filepath = os.path.split(os.path.abspath(__file__))[0]
    return os.path.normpath(os.path.join(filepath, '../../'))


@pytest.fixture(scope="session")
def datapath():
    """Example datasets for users."""
    return 'Examples/data'


@pytest.fixture(scope="session")
def testdatapath():
    """Smaller datasets for faster test execution."""
    return 'sfrmaker/test/data'


@pytest.fixture(scope="session")
def outdir():
    # output folder
    outdir = 'sfrmaker/test/temp/'
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    return outdir


@pytest.fixture(scope="session")
def bin_path(project_root_path):
    bin_path = os.path.join(project_root_path, "bin")
    if "linux" in platform.platform().lower():
        bin_path = os.path.join(bin_path, "linux")
    elif "darwin" in platform.platform().lower():
        bin_path = os.path.join(bin_path, "mac")
    else:
        bin_path = os.path.join(bin_path, "win")
    return bin_path


@pytest.fixture(scope="session")
def mf6_exe(bin_path):
    return os.path.join(bin_path, 'mf6')


@pytest.fixture(scope="session")
def mfnwt_exe(bin_path):
    return os.path.join(bin_path, 'mfnwt')


@pytest.fixture(scope="function")
def sfr_test_numbering():
    rd = pd.DataFrame()
    rd['i'] = [3, 4, 5,
               7, 8, 9,
               0, 1, 2,
               4, 4, 5,
               0, 0, 0,
               3, 4, 5,
               0, 1, 2,
               4, 5, 6,
               2, 2, 2]
    rd['j'] = [0, 1, 2,
               6, 6, 6,
               6, 6, 6,
               3, 4, 5,
               9, 8, 7,
               6, 6, 6,
               0, 0, 0,
               6, 6, 6,
               9, 8, 7]
    rd['iseg'] = sorted(list(range(1, 10)) * 3)
    rd['ireach'] = [1, 2, 3] * 9

    sd = pd.DataFrame()
    sd['nseg'] = range(1, 10)
    sd['outseg'] = [4, 0, 6, 8, 3, 8, 1, 2, 8]
    return rd, sd


@pytest.fixture(scope="function")
def sfr_testdata(sfr_test_numbering):
    rd, sd = sfr_test_numbering
    sd['width1'] = 1
    sd['width2'] = 1
    return sfrmaker.SFRData(reach_data=rd, segment_data=sd)


@pytest.fixture(scope='module')
def shellmound_simulation(testdatapath, outdir):
    sim = flopy.mf6.MFSimulation.load('mfsim', 'mf6', 'mf6', sim_ws='{}/shellmound/shellmound'.format(testdatapath))
    sim_ws = os.path.join(outdir, 'shellmound')
    if not os.path.isdir(sim_ws):
        os.makedirs(sim_ws)
    sim.sim_ws = sim_ws
    return sim


@pytest.fixture(scope='module')
def get_shellmound_model(shellmound_simulation):
    return shellmound_simulation.get_model('shellmound')


@pytest.fixture(scope='function')
def shellmound_model(get_shellmound_model):
    return copy.deepcopy(get_shellmound_model)


@pytest.fixture(scope='function')
def shellmound_grid(shellmound_model):
    m = shellmound_model
    sr = flopy.utils.SpatialReference(delr=m.dis.delr.array,  # cell spacing along a row
                                      delc=m.dis.delc.array,  # cell spacing along a column
                                      lenuni=2,  # model units of meters
                                      xll=500955.0, yll=1176285.0,  # lower left corner of model grid
                                      rotation=0,  # grid is unrotated
                                      proj4_str='epsg:5070'
                                      )
    m.sr = sr
    return sr


@pytest.fixture(scope='module')
def tyler_forks_grid_shapefile(datapath):
    return '{}/badriver/grid.shp'.format(datapath)


@pytest.fixture(scope='module')
def get_tylerforks_model(datapath, outdir):
    m = fm.Modflow.load('tf.nam', model_ws='{}/badriver/tylerforks'.format(datapath))
    model_ws = os.path.join(outdir, 'tylerforks')
    if not os.path.isdir(model_ws):
        os.makedirs(model_ws)
    m.model_ws = model_ws
    return m


@pytest.fixture(scope='function')
def tylerforks_model(get_tylerforks_model):
    m = copy.deepcopy(get_tylerforks_model)
    return m


@pytest.fixture(scope='function')
def tylerforks_model_grid(tyler_forks_grid_shapefile, tylerforks_model):
    m = tylerforks_model
    sr = flopy.utils.SpatialReference(delr=m.dis.delr.array,  # cell spacing along a row
                                      delc=m.dis.delc.array,  # cell spacing along a column
                                      lenuni=1,  # model units of feet
                                      xll=682688, yll=5139052,  # lower left corner of model grid
                                      rotation=0,  # grid is unrotated
                                      proj4_str='epsg:26715'
                                      # projected coordinate system of model (UTM NAD27 zone 15 North)
                                      )
    m.sr = sr
    return sr


@pytest.fixture(scope='module')
def lines_from_shapefile(testdatapath):
    flowlines_file = '{}/shellmound/flowlines.shp'.format(testdatapath)
    lns = sfrmaker.Lines.from_shapefile(flowlines_file,
                                        id_column='COMID',
                                        routing_column='tocomid',
                                        width1_column='width1',
                                        width2_column='width2',
                                        up_elevation_column='elevupsmo',
                                        dn_elevation_column='elevdnsmo',
                                        name_column='GNIS_NAME',
                                        attr_length_units='feet',  # units of source data
                                        attr_height_units='feet'  # units of source data
                                        )
    return lns


@pytest.fixture(scope='function')
def shellmound_sfrdata(shellmound_model, lines_from_shapefile,
                       shellmound_grid):
    m = shellmound_model
    # from the lines and StructuredGrid instances, make a sfrmaker.sfrdata instance
    # (lines are intersected with the model grid and converted to reaches, etc.)
    sfrdata = lines_from_shapefile.to_sfr(sr=shellmound_grid,
                                          model=m)
    return sfrdata
