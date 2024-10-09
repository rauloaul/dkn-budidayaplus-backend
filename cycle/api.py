from django.shortcuts import get_object_or_404
from ninja import Router
from pond.models import Pond
from .schemas import CycleInputSchema, CycleOutputSchema
from ninja_jwt.authentication import JWTAuth
from .models import Cycle, CycleFishDistribution
from ninja.errors import HttpError
from django.contrib.auth.models import User

router = Router()

@router.post('/', auth=JWTAuth(), response={200: CycleOutputSchema})
def create_cycle(request, payload: CycleInputSchema):
    pond_fish_amt_list = payload.pond_fish
    pond_fish_output = []
    supervisor = get_object_or_404(User, id=request.auth.id)
    try: 
        cycle = Cycle.objects.create(
            start_date=payload.start_date,
            end_date=payload.end_date,
            supervisor=supervisor
        )
    except:
        raise HttpError(400, "Tanggal selesai harus tepat 60 hari setelah tanggal mulai")

    try:
        for pond_fish_amount in pond_fish_amt_list:
            pond_id = pond_fish_amount.pond_id
            pond = Pond.objects.get(pond_id=pond_id)
            pond_fish = CycleFishDistribution.objects.create(
                cycle=cycle,
                pond=pond,
                fish_amount=pond_fish_amount.fish_amount
            )
            pond_fish_output.append(pond_fish)
    except:
        cycle.delete()
        raise HttpError(400, "Jumlah ikan harus lebih dari 0")
    
    return {
        "id": str(cycle.id),
        "start_date": cycle.start_date,
        "end_date": cycle.end_date,
        "supervisor": str(cycle.supervisor),
        "pond_fish": pond_fish_output
    }

@router.get("/", auth=JWTAuth(), response={200: CycleOutputSchema})
def get_cycle(request, id: str):
    return None

@router.delete("/{id}/", auth=JWTAuth())
def delete_cycle(request, id: str):
    return None

@router.put("/{id}/", auth=JWTAuth(), response={200: CycleOutputSchema})
def update_pond(request, id: str):
    return None