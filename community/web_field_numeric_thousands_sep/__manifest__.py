{
    'name': "Thousands Separator in Numeric Field",
    'summary': "Thousands Separator in Numeric Field",
    'author': 'Hoang Minh Hieu',
    'version': '18.0.1.0.1',
    'license': 'LGPL-3',
    'support': 'hieuhoangminh1996@gmail.com',
    'depends': ['web'],
    'data': [
    ],
    'assets': {
        'web.assets_web': [
            'web_field_numeric_thousands_sep/static/lib/autoNumeric/autoNumeric.js',

            'web_field_numeric_thousands_sep/static/src/thousands_sep_mixin.js',

            'web_field_numeric_thousands_sep/static/src/float/float_field.js',
            'web_field_numeric_thousands_sep/static/src/float/integer_field.js',
            'web_field_numeric_thousands_sep/static/src/float/monetary_field.js',
        ],
    },
    'images': ['static/description/main_screenshot.gif'],
}
