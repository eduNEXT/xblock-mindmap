
            (function(global){
                var MindMapI18N = {
                  init: function() {
                    

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = (n != 1);
    if (typeof v === 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  const newcatalog = {
    "(filtered from _MAX_ total entries)": "(filtrado de un total de _MAX_ registros)",
    "Actions": "Acciones",
    "Back": "Volver",
    "Cancel": "Cancelar",
    "Completed": "Completado",
    "Defines the number of points each problem is worth. If the value is not set, the problem is worth the sum of the option point values.": "Define el n\u00famero de puntos que vale cada problema. Si el valor no est\u00e1 establecido, el problema vale la suma de los valores de puntos de las opciones.",
    "Display name": "Nombre a mostrar",
    "False": "Falso",
    "Grade": "Calificaci\u00f3n",
    "Grade submissions": "Calificar env\u00edos",
    "Instructions for use": "Instrucciones de uso",
    "Invalid grade must be a number": "Calificaci\u00f3n inv\u00e1lida, debe ser un n\u00famero",
    "Is a static mindmap?": "\u00bfEs un mapa mental est\u00e1tico?",
    "Loading...": "Cargando...",
    "Maximum grade score given to assignment by instructors.": "Puntaje m\u00e1ximo de calificaci\u00f3n otorgado a la tarea por los instructores.",
    "Maximum score": "Puntaje m\u00e1ximo",
    "Mind map": "Mapa mental",
    "Mindmap body": "Contenido del mapa mental",
    "Mindmap student body": "Contenido del mapa mental del estudiante",
    "Mindmap submissions": "Env\u00edos de mapas mentales",
    "No data available in table": "Ning\u00fan dato disponible en esta tabla",
    "No matching records found": "No se encontraron resultados",
    "Not attempted": "No intentado",
    "Please enter a lower grade, maximum grade allowed is:": "Por favor ingresa una calificaci\u00f3n menor, la calificaci\u00f3n m\u00e1xima permitida es:",
    "Points": "Puntos",
    "Problem Weight": "Peso del problema",
    "Remove grade": "Eliminar calificaci\u00f3n",
    "Review": "Revisar",
    "Reviewing Mindmap for student: ": "Revisando Mapa Mental para el estudiante: ",
    "Save": "Guardar",
    "Save assignment": "Guardar asignaci\u00f3n",
    "Search": "Buscar",
    "Showing 0 to 0 of 0 entries": "Mostrando registros del 0 al 0 de un total de 0 registros",
    "Showing _START_ to _END_ of _TOTAL_ entries": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
    "Submission Status": "Estado del Env\u00edo",
    "Submission status": "Estado del env\u00edo",
    "Submit": "Enviar",
    "Submitted": "Enviado",
    "The body of the mind map. It is a dictionary with the following structure: {'root': {'text': 'Root', 'children': [{'text': 'Child 1', 'children': []}]}}": "El contenido del mapa mental. Es un diccionario con la siguiente estructura: {'root': {'text': 'Root', 'children': [{'text': 'Child 1', 'children': []}]}}",
    "The mind map that will be shown to students if the\"Is a static mindmap?\" field is set to \"True\"": "El mapa mental que se mostrar\u00e1 a los estudiantes si el campo \"\u00bfEs un mapa mental est\u00e1tico?\" est\u00e1 establecido en \"Verdadero\"",
    "The submission status of the assignment.": "El estado del env\u00edo de la tarea.",
    "True": "Verdadero",
    "Uploaded": "Subido",
    "Username": "Nombre de usuario",
    "Weight": "Peso",
    "Whether the mind map is static or not. If it is static, the instructor can create a mind map and it will be the same for all students. If it is not static, the students can create their own mind maps.": "Si el mapa mental es est\u00e1tico o no. Si es est\u00e1tico, el instructor puede crear un mapa mental y ser\u00e1 el mismo para todos los estudiantes. Si no es est\u00e1tico, los estudiantes pueden crear sus propios mapas mentales.",
    "With the keyboard": "Con el teclado",
    "With the mouse": "Con el mouse",
    "points": "puntos",
    "\u2192 Click the circle to expand or collapse the child nodes.": "\u2192 Haga clic en el c\u00edrculo para expandir o contraer los nodos hijos.",
    "\u2192 Ctrl + Enter: Create a new child node for the selected node.": "\u2192 Ctrl + Enter: Crear un nuevo nodo hijo para el nodo seleccionado.",
    "\u2192 Delete/Supr: Delete the selected node.": "\u2192 Delete/Supr: Eliminar el nodo seleccionado.",
    "\u2192 Double-click the node to edit it.": "\u2192 Doble clic en el nodo para editarlo.",
    "\u2192 Drag the node to move it.": "\u2192 Arrastre el nodo para moverlo.",
    "\u2192 Enter: Create a new brother node for the selected node.": "\u2192 Enter: Crear un nuevo nodo hermano para el nodo seleccionado.",
    "\u2192 F2: Edit the selected node.": "\u2192 F2: Editar el nodo seleccionado.",
    "\u2192 Space: Expand or collapse the selected node.": "\u2192 Espacio: Expandir o contraer el nodo seleccionado."
  };
  for (const key in newcatalog) {
    django.catalog[key] = newcatalog[key];
  }
  

  if (!django.jsi18n_initialized) {
    django.gettext = function(msgid) {
      const value = django.catalog[msgid];
      if (typeof value === 'undefined') {
        return msgid;
      } else {
        return (typeof value === 'string') ? value : value[0];
      }
    };

    django.ngettext = function(singular, plural, count) {
      const value = django.catalog[singular];
      if (typeof value === 'undefined') {
        return (count == 1) ? singular : plural;
      } else {
        return value.constructor === Array ? value[django.pluralidx(count)] : value;
      }
    };

    django.gettext_noop = function(msgid) { return msgid; };

    django.pgettext = function(context, msgid) {
      let value = django.gettext(context + '\x04' + msgid);
      if (value.includes('\x04')) {
        value = msgid;
      }
      return value;
    };

    django.npgettext = function(context, singular, plural, count) {
      let value = django.ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
      if (value.includes('\x04')) {
        value = django.ngettext(singular, plural, count);
      }
      return value;
    };

    django.interpolate = function(fmt, obj, named) {
      if (named) {
        return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
      } else {
        return fmt.replace(/%s/g, function(match){return String(obj.shift())});
      }
    };


    /* formatting library */

    django.formats = {
    "DATETIME_FORMAT": "N j, Y, P",
    "DATETIME_INPUT_FORMATS": [
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%m/%d/%Y %H:%M:%S",
      "%m/%d/%Y %H:%M:%S.%f",
      "%m/%d/%Y %H:%M",
      "%m/%d/%y %H:%M:%S",
      "%m/%d/%y %H:%M:%S.%f",
      "%m/%d/%y %H:%M"
    ],
    "DATE_FORMAT": "N j, Y",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%m/%d/%Y",
      "%m/%d/%y",
      "%b %d %Y",
      "%b %d, %Y",
      "%d %b %Y",
      "%d %b, %Y",
      "%B %d %Y",
      "%B %d, %Y",
      "%d %B %Y",
      "%d %B, %Y"
    ],
    "DECIMAL_SEPARATOR": ".",
    "FIRST_DAY_OF_WEEK": 0,
    "MONTH_DAY_FORMAT": "F j",
    "NUMBER_GROUPING": 0,
    "SHORT_DATETIME_FORMAT": "m/d/Y P",
    "SHORT_DATE_FORMAT": "m/d/Y",
    "THOUSAND_SEPARATOR": ",",
    "TIME_FORMAT": "P",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F Y"
  };

    django.get_format = function(format_type) {
      const value = django.formats[format_type];
      if (typeof value === 'undefined') {
        return format_type;
      } else {
        return value;
      }
    };

    /* add to global namespace */
    globals.pluralidx = django.pluralidx;
    globals.gettext = django.gettext;
    globals.ngettext = django.ngettext;
    globals.gettext_noop = django.gettext_noop;
    globals.pgettext = django.pgettext;
    globals.npgettext = django.npgettext;
    globals.interpolate = django.interpolate;
    globals.get_format = django.get_format;

    django.jsi18n_initialized = true;
  }
};


                  }
                };
                MindMapI18N.init();
                global.MindMapI18N = MindMapI18N;
            }(this));
        