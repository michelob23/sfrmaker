import pytest
from ..gis import CRS


# basic test that different input options don't crash CRS.__init__
@pytest.mark.parametrize('kwargs', ({},
                                    {'crs_dict': {'proj': 'utm',
                                                  'zone': 16,
                                                  'datum': 'NAD83',
                                                  'units': 'm',
                                                  'no_defs': None,
                                                  'type': 'crs'}},
                                    {'epsg': 26916},
                                    {'proj_str': 'epsg:26916'},
                                    {'prjfile': 'sfrmaker/test/data/shellmound/flowlines.prj'},
                                    {'crs_dict': {'epsg': 26916},
                                     'epsg': 26916,
                                     'proj_str': 'epsg:26916',
                                     'prjfile': 'sfrmaker/test/data/shellmound/flowlines.prj'
                                     }
)
                         )
def test_CRS(kwargs):
    # test init with no arguments
    crs = CRS(**kwargs)
    assert isinstance(crs, CRS)
    if len(kwargs) == 0:
        assert not crs.is_valid
    assert isinstance(crs.__repr__(), str)


def test_crs_eq():
    crs_4269_proj = CRS(proj_str='+proj=longlat +datum=NAD83 +no_defs ')
    crs_26715_epsg = CRS(epsg=26715)
    crs_26715_epsg_proj = CRS(proj_str='epsg:26715')
    crs_26715_proj = CRS(proj_str='+proj=utm +zone=15 +datum=NAD27 +units=m +no_defs ')
    crs_26715_prj = CRS(prjfile='Examples/data/badriver/grid.shp')
    assert crs_4269_proj != crs_26715_epsg
    assert crs_4269_proj != crs_26715_epsg_proj
    assert crs_4269_proj != crs_26715_proj
    assert crs_4269_proj != crs_26715_prj
    assert crs_26715_epsg == crs_26715_epsg_proj
    assert crs_26715_epsg == crs_26715_proj
    assert crs_26715_epsg == crs_26715_prj


def test_crs_units():
    crs_4269_proj = CRS(proj_str='+proj=longlat +datum=NAD83 +no_defs ')
    assert crs_4269_proj.length_units == 'degree'
    crs_26715_epsg = CRS(epsg=26715)
    assert crs_26715_epsg.length_units == 'meters'
    crs_26715_epsg_proj = CRS(proj_str='epsg:26715')
    assert crs_26715_epsg_proj.length_units == 'meters'
    crs_26715_proj = CRS(proj_str='+proj=utm +zone=15 +datum=NAD27 +units=m +no_defs ')
    assert crs_26715_proj.length_units == 'meters'
    crs_26715_prj = CRS(prjfile='Examples/data/badriver/grid.shp')
    assert crs_26715_prj.length_units == 'meters'


def test_is_valid():
    """
    With pyproj 2, all Proj instances are valid
    (error is raised in construction if not)
    https://github.com/pyproj4/pyproj/issues/304
    """
    crs_5070_epsg = CRS(epsg=5070)
    assert crs_5070_epsg.is_valid


@pytest.mark.xfail(reason="Invalid CRS class can't be instantiated")
def test_invalid():
    junk = CRS(proj_str='junk')
    assert not junk.is_valid


def test_crs_get_proj_str():
    crs_5070_epsg = CRS(epsg=5070)
    assert crs_5070_epsg.proj_str == 'EPSG:5070'


def test_rtree():
    from rtree import index