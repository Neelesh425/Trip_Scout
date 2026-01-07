from fastapi import APIRouter, HTTPException
from app.models import (
    SearchRequest, SearchResponse, BookingRequest, 
    BookingResponse, HistoryItem, AutonomousBookingRequest,
    AutonomousBookingResponse
)
from app.services.agent import TravelAgent
from typing import List
import asyncio

router = APIRouter()
agent = TravelAgent()

# In-memory storage for search history (use database in production)
search_history: List[HistoryItem] = []

@router.post("/api/search", response_model=SearchResponse)
async def search_flights(request: SearchRequest):
    """
    Search for flights based on user criteria
    """
    try:
        search_params = request.dict()
        response = await agent.process_search(search_params)
        
        # Add to history
        if response.status == "success":
            history_item = HistoryItem(
                search_id=response.search_id,
                search_params=search_params,
                timestamp=response.thoughts[-1].timestamp if response.thoughts else "",
                result_count=len(response.flights)
            )
            search_history.append(history_item)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/search-and-book", response_model=AutonomousBookingResponse)
async def search_and_book_autonomous(request: AutonomousBookingRequest):
    """
    Autonomous booking: Search for flights and automatically book the best option
    """
    try:
        search_params = request.search_params.dict()
        passenger_details = request.passenger_details
        
        result = await agent.process_search_and_book(search_params, passenger_details)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['message'])
        
        # Add to history
        history_item = HistoryItem(
            search_id=result['search_id'],
            search_params=search_params,
            timestamp=result['thoughts'][-1].timestamp if result['thoughts'] else "",
            result_count=len(result['all_flights'])
        )
        search_history.append(history_item)
        
        return AutonomousBookingResponse(
            search_id=result['search_id'],
            status=result['status'],
            thoughts=result['thoughts'],
            all_flights=result['all_flights'],
            selected_flight=result['selected_flight'],
            selection_reason=result['selection_reason'],
            booking_result=result['booking_result'],
            message=result['message']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/book", response_model=BookingResponse)
async def book_flight(request: BookingRequest):
    """
    Book a selected flight
    """
    try:
        result = await agent.make_booking(
            request.flight_id,
            request.passenger_details
        )
        
        return BookingResponse(
            booking_id=result['booking_id'],
            status=result['status'],
            confirmation_code=result.get('confirmation_code'),
            message=result['message']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/history", response_model=List[HistoryItem])
async def get_search_history():
    """
    Get search history
    """
    return search_history[-20:]  # Return last 20 searches

@router.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "message": "Travel booking agent is running"}