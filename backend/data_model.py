data_model = {
    'hospital_name': {
        '__type__': 'SeriesDataModelUnique',
        'series_name': 'Hospital name'
    },
    'date_of_birth': {
        '__type__': 'SeriesDataModelDate',
        'series_name': 'Date of birth'
    },
    'date_of_diagnosis': {
        '__type__': 'SeriesDataModelDate',
        'series_name': 'Date of diagnosis'
    },
    'sex': {
        '__type__': 'SeriesDataModelCategorical',
        'series_name': 'Sex',
        'list_value': ['male', 'female']
    },
    'race': {
        '__type__': 'SeriesDataModelCategorical',
        'series_name': 'Race',
        'list_value': ['White', 'Black or African American', 'Asian', 'Hispanic or Latino', 'American Indian or Alaska Native', 'Native Hawaiian or Other Pacific Islander']
    },
    'ethnicity': {
        '__type__': 'SeriesDataModelCategorical',
        'series_name': 'Ethnicity',
        'list_value': ['Not Hispanic or Latino', 'Hispanic or Latino']
    },
    'socioeconomic': {
        '__type__': 'SeriesDataModelCategorical',
        'series_name': 'Socioeconomic',
        'list_value': ['Middle class', 'Lower middle class', 'Upper middle class', 'Lower class', 'Upper class']
    },
    'rurality': {
        '__type__': 'SeriesDataModelCategorical',
        'series_name': 'Rurality',
        'list_value': ['Metropolitan', 'Micropolitan', 'Small town', 'Rural']
    },
    'date_of_death': {
        '__type__': 'SeriesDataModelDate',
        'series_name': 'Date of death'
    },
}