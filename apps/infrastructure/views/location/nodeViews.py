# standard library
import json, time

# Django
from django.http import JsonResponse, HttpResponseBadRequest
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point,Polygon, MultiPolygon, GEOSGeometry
from django.core.serializers import serialize
from django.utils.decorators import method_decorator

# local Django
from apps.infrastructure.models import Node, District

class NodeInDistrictView(View):
    """
    Buscar todos los nodos de un conjunto de uno, o mas barrios
    """
    def get(self, request, *args, **kwargs):
        try:
            district = int(request.GET.get("disrict"))
            start_time = time.time()
            nodes = Node.objects.filter(fk_district__id = district)

            data= {
                    'type':'success',
                    'data': [{'pk': node.pk,
                            'painting_code': node.painting_code,
                            'fk_district': district,
                            'lng': node.location.x,
                            'lat': node.location.y} for node in nodes]}
        except Exception as e:
            data= {'type':'error', 'msg': str(e)}
        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)

class NodeSearchPaintingCode(View):
    """
    Buscar nodos por el codigo de pintado
    """
    def get(self, request, painting_code, *args, **kwargs):
        try:
            start_time = time.time()
            nodes = Node.objects.filter(painting_code=painting_code)

            if not nodes.exists():
                raise Exception('No se encontraron nodos con el codigo de pintado suministrado')
            
            data= {
                'type':'success',
                'data': [{'pk': node.pk,
                          'painting_code': node.painting_code,
                          'comuna': node.fk_district.fk_comuna.name if node.fk_district else None,
                          'district': node.fk_district.name if node.fk_district else None,
                          'lng': node.location.x,
                          'lat': node.location.y} for node in nodes]}
        except Exception as e:
            data= {'type':'error', 'msg': str(e)}
        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)
   
class NodeSearchId(View):
    """
    Buscar nodos por ID
    """
    instance = lambda self, id: get_object_or_404(Node, id=id)

    serialize = lambda self, node: [{'pk': node.pk,
                                    'painting_code': node.painting_code,
                                    'district': node.fk_district.name,
                                    'comuna': node.fk_district.fk_comuna.name,
                                    'lng': node.location.x,
                                    'lat': node.location.y}]

    def get(self, request, id, *args, **kwargs):
        start_time = time.time()

        instance = self.instance(id)
        data = {'type': 'success', 
                'data': self.serialize(instance)}

        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)

class NodeSearchInArea(View):
    """
    Buscar nodos en un area partir de un punto
    """
    def get(self, request,*args, **kwargs):
        start_time = time.time()

        longitud = request.GET.get("lng")
        latitud = request.GET.get("lat")
        node_data = []

        if latitud and longitud:
            punto = GEOSGeometry(f'POINT({longitud} {latitud})', srid=4326)

            distante = 0.0010
            queryset = Node.objects.filter(location__distance_lte=(punto, distante))

            # Especifica los campos que deseas incluir en la serialización
            fields_to_select = ['pk', 'location', 'painting_code','fk_district']
            
            node_data = serialize(
                "geojson",
                queryset=queryset,
                fields=fields_to_select, 
                geometry_field="location",
            )
            dataProperties = json.loads(node_data)

            for feature in dataProperties['features']:
                district_id = feature['properties']['fk_district']
                locationQueryset = District.objects.filter(id=district_id).values('name', 'fk_comuna__name')

                for element in list(locationQueryset):
                    feature['properties'].update(element)

        else:
            errorValue= {}
            errorValue['type']='error'
            errorValue['msg']='No ha ingresado una coordenada valida para la consulta'

            node_data.append(errorValue)
        return JsonResponse(json.dumps(dataProperties), safe=False)

class SearchInfratructureInNodeView(LoginRequiredMixin,View):
    """
    Buscar toda la infraestructura asociada a un nodo en particular
    """
    def get(self, request, pk, *args, **kwargs):
        try:
            data = dict()
            node = Node.objects.get(pk=pk)

            apboxes = [obj.toJSON() for obj in node.apbox_set.all()]
            trafos = [obj.toJSON() for obj in node.trafo_set.all()]
            luminaires = [obj.toJSON() for obj in node.luminaire_set.all()]
            supports = [obj.toJSON() for obj in node.support_set.all()]

            data['type']= 'success'
            data['data'] = {
                'apbox': apboxes,
                'trafo': trafos,
                'Luminaire': luminaires,
                'Support': supports,
            }
        except Exception as e:
            data['type']='error'
            data['msg']= str(e)
        return JsonResponse(data, safe=False)


class NodeSearchComunaView(View):
    def get(self, request, *args, **kwargs):
        try:
            start_time = time.time()
            comuna = request.GET.get("comuna")

            nodes = Node.objects.filter(fk_district__fk_comuna__id = int(comuna))
            data= {
                'type':'success',
                'data': [{'pk': node.pk,
                          'painting_code': node.painting_code,
                          'lng': node.location.x,
                          'lat': node.location.y} for node in nodes]}
        except Exception as e:
            data= {'type':'error', 'msg': str(e)}
        data['time'] = str(time.time() - start_time)
        return JsonResponse(data, safe=False)
