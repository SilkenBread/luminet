from collections import defaultdict
from django.contrib.auth.models import Group
from django.db.models import Prefetch
from .models import MenuGroupItem, MenuGroup, MenuItem

def build_tree(flat_items):
    """
    Construye una estructura de árbol jerárquica a partir de una lista plana de items.
    """
    by_parent = defaultdict(list)
    for item in flat_items:
        by_parent[item.parent_id].append(item)

    def attach_children(node):
        # Filtrar hijos únicos por id
        seen = set()
        unique_children = []
        for child in by_parent.get(node.id, []):
            if child.id not in seen:
                unique_children.append(child)
                seen.add(child.id)
        children = [attach_children(child) for child in unique_children]
        return {"obj": node, "children": children}

    # Elementos de nivel superior (sin padre)
    return [attach_children(root) for root in by_parent.get(None, [])]

def menu_items_for_user(request):
    """
    Context processor que agrega la estructura de menú al contexto de las plantillas.
    """
    user = request.user
    user_groups = set(user.groups.all()) if user.is_authenticated else set()

    # Obtener grupos de menú visibles para el usuario
    if user.is_superuser or user.groups.filter(name='Administrador').exists():
        visible_menus = MenuGroup.objects.all()
    elif user_groups:
        visible_menus = MenuGroup.objects.filter(allowed_groups__in=user_groups).distinct()
    else:
        visible_menus = MenuGroup.objects.filter(allowed_groups=None) | MenuGroup.objects.filter(allowed_groups__isnull=True)

    # Obtener items ordenados por grupo
    through = (
        MenuGroupItem.objects
        .filter(menu_group__in=visible_menus)
        .select_related('menu_item', 'menu_group', 'menu_item__parent')
        .order_by('menu_group_id', 'order')
    )

    # Crear una lista de todos los items visibles
    visible_items = []
    for row in through:
        visible_items.append(row.menu_item)

    # Filtrar items raíz únicos (sin padre)
    unique_root_items = {}
    for item in visible_items:
        if item.parent_id is None:
            unique_root_items[item.id] = item
    # Agregar también los hijos (no raíz)
    non_root_items = [item for item in visible_items if item.parent_id is not None]
    all_items = list(unique_root_items.values()) + non_root_items

    # Construir el árbol de items
    tree = build_tree(all_items)
    
    # Agregar el atributo children_filtered a cada item
    for item in tree:
        item['obj'].children_filtered = [child['obj'] for child in item['children']]
        for child in item['children']:
            child['obj'].children_filtered = [grandchild['obj'] for grandchild in child['children']]
    
    # Devolver la lista de items raíz como main_menu_items
    return {"main_menu_items": [item['obj'] for item in tree]}