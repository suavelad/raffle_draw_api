

from rest_framework.views import exception_handler

def custom_exception_handler(exec, context):
    handlers = {
        'ValidationError': _handle_generic_error,
        'Http404': _handle_generic_error,
    }
    response = exception_handler(exec,context)
    exception_class = exec.__class__.__name__
    
    
    if response is not None:
        response.data['status_code']= response.status_code
    
    if exception_class in handlers:
        return handlers[exception_class](exec,context,response)
    return response
    
    
    

def _handle_generic_error(exec, context,response):
    return response
