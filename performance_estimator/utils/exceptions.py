class TableNotFoundError(Exception):
    
    def __init__(self,table_type):
        super().__init__(f'{table_type} table not found in the HTML page.') 


class PageCouldNotBeRetrievedError(Exception):
    
    def __init__(self,page_type,status_code):
        super().__init__(f'Failed to retrieve the {page_type} page. Status code: {status_code}') 