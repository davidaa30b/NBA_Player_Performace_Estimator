def sanitize_data(data_dict,int_fields,float_fields):
    for key, value in data_dict.items():
        if key in int_fields and value == '':  
            data_dict[key] = 0
        elif key in float_fields and value == '':  
            data_dict[key] = 0.0
    return data_dict

def retrive_data_for_columns_from_table(columns,cols):
    return {
        columns[i]: (int(cols[i-1].text.strip()) if cols[i-1].text.strip().isdigit() else
                     (float(cols[i-1].text.strip()) if '.' in cols[i-1].text.strip() else
                      cols[i-1].text.strip()))
                      for i in range(2, len(columns))
                      }