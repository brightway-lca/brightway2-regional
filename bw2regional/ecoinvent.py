# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from . import faces
from bw2data import databases, Database, geomapping
from constructive_geometries import ConstructiveGeometries
import json
import pprint
import pyprind


def discretize_rest_of_world(database, warn=True):
    """Create new locations for each unique rest of the world (RoW). A RoW location is defined by the topological faces that aren't covered by a specific market.

    We define a product system by the combination of name and reference product. For each product system, we find the locations where markets are defined. In some cases, only a global market is present, or there is no RoW market because certain products are only available in certain places. However, there will be a RoW market for most product systems in ecoinvent.

    We start by creating two dictionaries:

        * ``locations``: {``name`` + ``reference product``: [list of locations]
        * ``activities``: {key: ``name`` + ``reference product`` if ``location`` == ``RoW``}

    Then process ``locations`` and include only location lists where ``RoW`` is present.

    Then create and label the unique set of RoW locations in another dictionary:

        * ``row_locations``: {frozenset([locations]): ``RoW-X``} where X is an counter

    We can then go through ``activities``, look up the list of locations in ``locations``, and get the specific RoW name in ``row_locations``.

    """
    assert database in databases, "Unknown database"

    database = Database(database)
    locations = {}
    activities = {}
    exceptions = []

    for ds in database:
        label = ds['name'] + ":" + ds['reference product']
        locations.setdefault(label, []).append(ds['location'])
        if ds['location'] == 'RoW':
            activities[ds.key] = label

    for key, value in locations.items():
        if "GLO" in value:
            assert value == ["GLO"], "Market {} include GLO location".format(key)
        elif "RoW" not in value:
            exceptions.append(key)

    if exceptions and warn:
        print("Can't find `RoW` location in the following markets. This is not necessarily an error!")
        pprint.pprint(exceptions)

    locations = {k: v for k, v in locations.items() if 'RoW' in v}

    for k, v in locations.items():
        assert len(v) == len(set(v)), \
            "Locations repeated in market {}: {}".format(k, v)

    row_locations = {frozenset(obj): "RoW-{}".format(index)
        for index, obj in enumerate({tuple(sorted(x)) for x in locations.values()})
    }

    labels = {}

    for act_key, act_location in activities.items():
        labels[act_key] = row_locations[frozenset(locations[act_location])]

    return labels, row_locations, locations


LOCATION_CORRESPONDENCE = {
    u'AD': u'Andorra',
    u'AE': u'United Arab Emirates',
    u'AF': u'Afghanistan',
    u'AG': u'Antigua and Barbuda',
    u'AI': u'Anguilla',
    u'AL': u'Albania',
    u'AM': u'Armenia',
    u'AO': u'Angola',
    u'AQ': u'Antarctica',
    u'AR': u'Argentina',
    u'AS': u'American Samoa',
    u'ASCC': u'Alaska Systems Coordinating Council',
    u'AT': u'Austria',
    u'AU': u'Australia',
    u'AUS-ACT': u'Australian Capital Territory',
    u'AUS-NSW': u'New South Wales',
    u'AUS-NTR': u'Northern Territory',
    u'AUS-QNS': u'Queensland',
    u'AUS-SAS': u'South Australia',
    u'AUS-TSM': u'Tasmania',
    u'AUS-VCT': u'Victoria',
    u'AUS-WAS': u'Western Australia',
    u'AW': u'Aruba',
    u'AX': u'\xc5land Islands',
    u'AZ': u'Azerbaijan',
    u'Aluminium producing area, EU27 and EFTA countries': u'IAI Area, EU27 & EFTA',
    u'Aluminium producing area, Europe outside EU27 and EFTA': u'IAI Area, Europe outside EU & EFTA',
    u'Asia without China': u'Asia without China',
    u'BA': u'Bosnia and Herzegovina',
    u'BALTSO': u'Baltic System Operator',
    u'BB': u'Barbados',
    u'BD': u'Bangladesh',
    u'BE': u'Belgium',
    u'BF': u'Burkina Faso',
    u'BG': u'Bulgaria',
    u'BH': u'Bahrain',
    u'BI': u'Burundi',
    u'BJ': u'Benin',
    u'BL': u'Saint Barthelemy',
    u'BM': u'Bermuda',
    u'BN': u'Brunei Darussalam',
    u'BO': u'Bolivia, Plurinational State of',
    u'BQ': u'Bonaire, Sint Eustatius, and Saba',
    u'BR': u'Brazil',
    u'BS': u'Bahamas',
    u'BT': u'Bhutan',
    u'BV': u'Bouvet Island',
    u'BW': u'Botswana',
    u'BY': u'Belarus',
    u'BZ': u'Belize',
    u'CA': u'Canada',
    u'CA-AB': u'Alberta',
    u'CA-BC': u'British Columbia',
    u'CA-MB': u'Manitoba',
    u'CA-NB': u'New Brunswick',
    u'CA-NF': u'Newfoundland and Labrador',
    u'CA-NS': u'Nova Scotia',
    u'CA-NT': u'Northwest Territories',
    u'CA-NU': u'Nunavut',
    u'CA-ON': u'Ontario',
    u'CA-PE': u'Prince Edward Island',
    u'CA-QC': u'Qu\xe9bec',
    u'CA-SK': u'Saskatchewan',
    u'CA-YK': u'Yukon',
    u'CC': u'Cocos (Keeling) Islands',
    u'CD': u'Congo, Democratic Republic of the',
    u'CENTREL': u'Central European Power Association',
    u'CF': u'Central African Republic',
    u'CG': u'Congo',
    u'CH': u'Switzerland',
    u'CI': u"Cote d'Ivoire",
    u'CK': u'Cook Islands',
    u'CL': u'Chile',
    u'CM': u'Cameroon',
    u'CN': u'China',
    u'CO': u'Colombia',
    u'CR': u'Costa Rica',
    u'CS': u'Serbia and Montenegro',
    u'CU': u'Cuba',
    u'CV': u'Cape Verde',
    u'CW': u'Cura\xe7ao',
    u'CX': u'Christmas Island',
    u'CY': u'Cyprus',
    u'CZ': u'Czech Republic',
    u'Canada without Alberta': u'Canada without Alberta',
    u'Canada without Alberta and Quebec': u'Canada without Alberta and Quebec',
    u'Canary Islands': u'Canary Islands',
    u'Central Asia': u'Central Asia',
    u'China Southern Power Grid': u'CSG',
    u'DE': u'Germany',
    u'DJ': u'Djibouti',
    u'DK': u'Denmark',
    u'DM': u'Dominica',
    u'DO': u'Dominican Republic',
    u'DZ': u'Algeria',
    u'EC': u'Ecuador',
    u'EE': u'Estonia',
    u'EEU': u'Central and Eastern Europe',
    u'EG': u'Egypt',
    u'EH': u'Western Sahara',
    u'ENTSO-E': u'European Network of Transmission Systems Operators for Electricity',
    u'ER': u'Eritrea',
    u'ES': u'Spain',
    u'ET': u'Ethiopia',
    u'Europe without NORDEL (NCPA)': u'Europe without NORDEL (NCPA)',
    u'Europe without Switzerland': u'Europe without Switzerland',
    u'Europe, without Russia and Turkey': u'Europe, without Russia and Turkey',
    u'FI': u'Finland',
    u'FJ': u'Fiji',
    u'FK': u'Falkland Islands (Malvinas)',
    u'FM': u'Micronesia, Federated States of',
    u'FO': u'Faroe Islands',
    u'FR': u'France',
    u'FRCC': u'Florida Reliability Coordinating Council',
    u'FSU': u'Commonwealth of Independent States',
    u'France, including overseas territories': u'France, including overseas territories',
    u'GA': u'Gabon',
    u'GB': u'United Kingdom',
    u'GD': u'Grenada',
    u'GE': u'Georgia',
    u'GF': u'French Guiana',
    u'GG': u'Guernsey',
    u'GH': u'Ghana',
    u'GI': u'Gibraltar',
    u'GL': u'Greenland',
    # u'GLO': u'Global',
    u'Global': u'GLO',
    u'GM': u'Gambia',
    u'GN': u'Guinea',
    u'GP': u'Guadeloupe',
    u'GQ': u'Equatorial Guinea',
    u'GR': u'Greece',
    u'GS': u'South Georgia and the South Sandwich Islands',
    u'GT': u'Guatemala',
    u'GU': u'Guam',
    u'GW': u'Guinea-Bissau',
    u'GY': u'Guyana',
    u'HICC': u'HICC',
    u'HK': u'Hong Kong',
    u'HM': u'Heard Island and McDonald Islands',
    u'HN': u'Honduras',
    u'HR': u'Croatia',
    u'HT': u'Haiti',
    u'HU': u'Hungary',
    u'IAI Area 1': u'IAI producing Area 1, Africa',
    u'IAI Area 2, North America': u'IAI producing Area 2, North America',
    u'IAI Area 2, without Quebec': u'IAI producing Area 2, North America, without Quebec',
    u'IAI Area 3': u'IAI producing Area 3, South America',
    u'IAI Area 4&5 without China': u'IAI producing Area 4 and 5, South and East Asia, without China',
    u'IAI Area 6, Europe': u'IAI producing Area 6A&B, West, East, and Central Europe',
    u'IAI Area 8': u'IAI producing Area 8, Gulf Region',
    u'ID': u'Indonesia',
    u'IE': u'Ireland',
    u'IL': u'Israel',
    u'IM': u'Isle of Man',
    u'IN': u'India',
    u'IO': u'British Indian Ocean Territory',
    u'IQ': u'Iraq',
    u'IR': u'Iran',
    u'IS': u'Iceland',
    u'IT': u'Italy',
    u'JE': u'Jersey',
    u'JM': u'Jamaica',
    u'JO': u'Jordan',
    u'JP': u'Japan',
    u'KE': u'Kenya',
    u'KG': u'Kyrgyzstan',
    u'KH': u'Cambodia',
    u'KI': u'Kiribati',
    u'KM': u'Comoros',
    u'KN': u'Saint Kitts and Nevis',
    u'KP': u"Korea, Democratic People's Republic of",
    u'KR': u'South Korea',
    u'KW': u'Kuwait',
    u'KY': u'Cayman Islands',
    u'KZ': u'Kazakhstan',
    u'LA': u"Lao People's Democratic Republic",
    u'LB': u'Lebanon',
    u'LC': u'Saint Lucia',
    u'LI': u'Liechtenstein',
    u'LK': u'Sri Lanka',
    u'LR': u'Liberia',
    u'LS': u'Lesotho',
    u'LT': u'Lithuania',
    u'LU': u'Luxembourg',
    u'LV': u'Latvia',
    u'LY': u'Libya',
    u'MA': u'Morocco',
    u'MC': u'Monaco',
    u'MD': u'Moldova, Republic of',
    u'ME': u'Montenegro',
    u'MF': u'Saint Martin',
    u'MG': u'Madagascar',
    u'MH': u'Marshall Islands',
    u'MK': u'Macedonia',
    u'ML': u'Mali',
    u'MM': u'Myanmar',
    u'MN': u'Mongolia',
    u'MO': u'Macau',
    u'MP': u'Northern Mariana Islands',
    u'MQ': u'Martinique',
    u'MR': u'Mauritania',
    u'MRO': u'Midwest Reliability Organization',
    u'MRO, US only': u'Midwest Reliability Organization, US part only',
    u'MS': u'Montserrat',
    u'MT': u'Malta',
    u'MU': u'Mauritius',
    u'MV': u'Maldives',
    u'MW': u'Malawi',
    u'MX': u'Mexico',
    u'MY': u'Malaysia',
    u'MZ': u'Mozambique',
    u'NA': u'Namibia',
    u'NAFTA': u'North American Free Trade Agreement',
    u'NC': u'New Caledonia',
    u'NE': u'Niger',
    u'NF': u'Norfolk Island',
    u'NG': u'Nigeria',
    u'NI': u'Nicaragua',
    u'NL': u'Netherlands',
    u'NO': u'Norway',
    u'NORDEL': u'Nordic Countries Power Association',
    u'NP': u'Nepal',
    u'NPCC': u'Northeast Power Coordinating Council',
    u'NPCC, US only': u'Northeast Power Coordinating Council, US part only',
    u'NR': u'Nauru',
    u'NU': u'Niue',
    u'NZ': u'New Zealand',
    u'OM': u'Oman',
    u'PA': u'Panama',
    u'PE': u'Peru',
    u'PF': u'French Polynesia',
    u'PG': u'Papua New Guinea',
    u'PH': u'Philippines',
    u'PK': u'Pakistan',
    u'PL': u'Poland',
    u'PM': u'Saint Pierre and Miquelon',
    u'PN': u'Pitcairn',
    u'PR': u'Puerto Rico',
    u'PS': u'Palestinian Territory, Occupied',
    u'PT': u'Portugal',
    u'PW': u'Palau',
    u'PY': u'Paraguay',
    u'QA': u'Qatar',
    u'Qu\xe9bec, HQ distribution network': u'Qu\xe9bec, Hydro-Qu\xe9bec distribution network',
    u'RAF': u'Africa',
    u'RAS': u'Asia',
    u'RE': u'Reunion',
    u'RER': u'Europe',
    u'RER w/o AT+BE+CH+DE+FR+IT': u'Europe without Austria, Belgium, France, Germany, Italy, Liechtenstein, Monaco, San Marino, Switzerland, and the Vatican',
    u'RER w/o CH+DE': u'Europe without Germany and Switzerland',
    u'RER w/o DE+NL+NO': u'Europe without Germany, the Netherlands, and Norway',
    u'RFC': u'ReliabilityFirst Corporation',
    u'RLA': u'Latin America and the Caribbean',
    u'RME': u'Middle East',
    u'RNA': u'Northern America',
    u'RO': u'Romania',
    u'RS': u'Serbia',
    u'RU': u'Russia',
    u'RW': u'Rwanda',
    # u'RoW': u'Rest-of-World',
    u'Rest-of-World': u'RoW',
    u'SA': u'Saudi Arabia',
    u'SAS': u'South Asia',
    u'SB': u'Solomon Islands',
    u'SC': u'Seychelles',
    u'SD': u'Sudan',
    u'SE': u'Sweden',
    u'SERC': u'SERC Reliability Corporation',
    u'SG': u'Singapore',
    u'SH': u'Saint Helena',
    u'SI': u'Slovenia',
    u'SJ': u'Svalbard and Jan Mayen',
    u'SK': u'Slovakia',
    u'SL': u'Sierra Leone',
    u'SM': u'San Marino',
    u'SN': u'Senegal',
    u'SO': u'Somalia',
    u'SPP': u'Southwest Power Pool',
    u'SR': u'Suriname',
    u'SS': u'South Sudan',
    u'ST': u'Sao Tome and Principe',
    u'SV': u'El Salvador',
    u'SX': u'Sint Maarten',
    u'SY': u'Syrian Arab Republic',
    u'SZ': u'Swaziland',
    u'Spain, including overseas territories': u'Spain, including overseas territories',
    u'State Grid Corporation of China': u'SGCC',
    u'TC': u'Turks and Caicos Islands',
    u'TD': u'Chad',
    u'TF': u'French Southern Territories',
    u'TG': u'Togo',
    u'TH': u'Thailand',
    u'TJ': u'Tajikistan',
    u'TK': u'Tokelau',
    u'TL': u'Timor-Leste',
    u'TM': u'Turkmenistan',
    u'TN': u'Tunisia',
    u'TO': u'Tonga',
    u'TR': u'Turkey',
    u'TRE': u'Texas Regional Entity',
    u'TT': u'Trinidad and Tobago',
    u'TV': u'Tuvalu',
    u'TW': u'Taiwan',
    u'TZ': u'Tanzania',
    u'UA': u'Ukraine',
    u'UCTE': u'Union for the Co-ordination of Transmission of Electricity',
    u'UCTE without France': u'UCTE without France',
    u'UCTE without Germany': u'UCTE without Germany',
    u'UCTE without Germany and France': u'UCTE without Germany and France',
    u'UG': u'Uganda',
    u'UM': u'United States Minor Outlying Islands',
    u'UN-AMERICAS': u'Americas',
    u'UN-ASIA': u'Asia, UN Region',
    u'UN-AUSTRALIANZ': u'Australia and New Zealand',
    u'UN-CAMERICA': u'Central America',
    u'UN-EAFRICA': u'Eastern Africa',
    u'UN-EASIA': u'Eastern Asia',
    u'UN-EEUROPE': u'Eastern Europe',
    u'UN-EUROPE': u'Europe, UN Region',
    u'UN-MAFRICA': u'Middle Africa',
    u'UN-MELANESIA': u'Melanesia',
    u'UN-MICRONESIA': u'Micronesia',
    u'UN-NAFRICA': u'Northern Africa',
    u'UN-NEUROPE': u'Northern Europe',
    u'UN-OCEANIA': u'Oceania',
    u'UN-POLYNESIA': u'Polynesia',
    u'UN-SAMERICA': u'South America',
    u'UN-SASIA': u'Southern Africa',
    u'UN-SEASIA': u'South-Eastern Asia',
    u'UN-SEUROPE': u'Southern Europe',
    u'UN-WAFRICA': u'Western Africa',
    u'UN-WASIA': u'Western Asia',
    u'US': u'United States of America',
    u'UY': u'Uruguay',
    u'UZ': u'Uzbekistan',
    u'VA': u'Holy See (Vatican City State)',
    u'VC': u'Saint Vincent and the Grenadines',
    u'VE': u'Venezuela',
    u'VG': u'Virgin Islands, British',
    u'VI': u'Virgin Islands, U.S.',
    u'VN': u'Viet Nam',
    u'VU': u'Vanuatu',
    u'WECC': u'Western Electricity Coordinating Council',
    u'WECC, US only': u'Western Electricity Coordinating Council, US part only',
    u'WEU': u'Western Europe',
    u'WF': u'Wallis and Futuna',
    u'WS': u'Samoa',
    u'YE': u'Yemen',
    u'YT': u'Mayotte',
    u'ZA': u'South Africa',
    u'ZM': u'Zambia',
    u'ZW': u'Zimbabwe'
}

def fix_ecoinvent_location_names(name):
    assert name in databases, "Unknown database"
    for act in pyprind.prog_bar(Database(name)):
        try:
            act['location'] = LOCATION_CORRESPONDENCE[act['location']]
            act.save()
        except KeyError:
            pass



def prepare_ecoinvent_database(name):
    def _(obj):
        return (x for x in obj if x != "RoW")

    assert name in databases, "Unknown database"

    cg = ConstructiveGeometries()
    db = Database(name)
    searchable = db._searchable
    if searchable:
        db.make_unsearchable()

    print("Fixing ecoinvent location names")
    geomapping.add(list(LOCATION_CORRESPONDENCE.values()))
    fix_ecoinvent_location_names(name)

    print("Fixing rest of the world locations")
    labels, row_locations, locations = discretize_rest_of_world(name, False)
    geomapping.add(list(labels.values()))
    for key, place in pyprind.prog_bar(labels.items()):
        act = db.get(key[1])
        act['location'] = place
        act.save()

    print("Defining different rest of the world locations")
    row_topo = {name: cg.construct_rest_of_world(list(_(places)), geom=False) for places, name in row_locations.items()}
    faces.update({k: [('ecoinvent-topology', fid) for fid in v]
                      for k, v in row_topo.items()})
    db.process()

    if searchable:
        db.make_searchable()
