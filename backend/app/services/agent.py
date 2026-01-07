from typing import List, Dict, Any
from datetime import datetime
import asyncio
from app.services.llm_client import LLMClient
from app.services.flight_api import FlightAPI
from app.models import AgentThought, SearchResponse, Flight, BookingResponse
import uuid

class TravelAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.flight_api = FlightAPI()
        self.thoughts: List[AgentThought] = []
    
    def _add_thought(self, thought: str, action: str):
        """Add a thought to the agent's thinking process"""
        self.thoughts.append(AgentThought(
            step=len(self.thoughts) + 1,
            thought=thought,
            action=action,
            timestamp=datetime.now().isoformat()
        ))
    
    async def process_search(self, search_params: Dict[str, Any]) -> SearchResponse:
        """
        Main agent loop to process a flight search request
        """
        self.thoughts = []  # Reset thoughts for new search
        search_id = str(uuid.uuid4())
        
        try:
            # Step 1: Analyze the search intent
            self._add_thought(
                "Analyzing search parameters and user intent",
                "analyze_intent"
            )
            await asyncio.sleep(0.5)  # Simulate thinking time
            
            intent_analysis = await self.llm.analyze_search_intent(search_params)
            
            # Step 2: Validate search parameters
            self._add_thought(
                f"Validating search parameters. Strategy: {intent_analysis.get('search_strategy')}",
                "validate_params"
            )
            await asyncio.sleep(0.3)
            
            validation_result = self._validate_params(search_params)
            if not validation_result['valid']:
                return SearchResponse(
                    search_id=search_id,
                    status="error",
                    thoughts=self.thoughts,
                    flights=[],
                    message=validation_result['message'],
                    search_params=search_params
                )
            
            # Step 3: Search for flights
            self._add_thought(
                f"Searching for flights from {search_params['origin']} to {search_params['destination']}",
                "search_flights"
            )
            await asyncio.sleep(0.5)
            
            flights = await self.flight_api.search_flights(search_params)
            
            # Step 4: Analyze results
            self._add_thought(
                f"Found {len(flights)} flights. Analyzing best options based on price and convenience",
                "analyze_results"
            )
            await asyncio.sleep(0.4)
            
            # Step 5: Generate summary
            summary = await self.llm.generate_search_summary([f.dict() for f in flights])
            
            self._add_thought(
                "Search completed successfully. Presenting results to user",
                "complete"
            )
            
            return SearchResponse(
                search_id=search_id,
                status="success",
                thoughts=self.thoughts,
                flights=flights,
                message=summary,
                search_params=search_params
            )
            
        except Exception as e:
            self._add_thought(
                f"Error occurred: {str(e)}",
                "error"
            )
            return SearchResponse(
                search_id=search_id,
                status="error",
                thoughts=self.thoughts,
                flights=[],
                message=f"An error occurred while processing your request: {str(e)}",
                search_params=search_params
            )
    
    async def process_search_and_book(self, search_params: Dict[str, Any], passenger_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Autonomous agent: Search for flights and automatically book the best option
        """
        self.thoughts = []  # Reset thoughts for new search
        search_id = str(uuid.uuid4())
        
        try:
            # Step 1: Analyze the search intent
            self._add_thought(
                "Analyzing search parameters and user intent for autonomous booking",
                "analyze_intent"
            )
            await asyncio.sleep(0.5)
            
            intent_analysis = await self.llm.analyze_search_intent(search_params)
            
            # Step 2: Validate search parameters
            self._add_thought(
                f"Validating search parameters. Strategy: {intent_analysis.get('search_strategy')}",
                "validate_params"
            )
            await asyncio.sleep(0.3)
            
            validation_result = self._validate_params(search_params)
            if not validation_result['valid']:
                return {
                    "status": "error",
                    "message": validation_result['message'],
                    "thoughts": self.thoughts
                }
            
            # Step 3: Search for flights
            self._add_thought(
                f"Searching for flights from {search_params['origin']} to {search_params['destination']}",
                "search_flights"
            )
            await asyncio.sleep(0.5)
            
            flights = await self.flight_api.search_flights(search_params)
            
            if not flights:
                self._add_thought(
                    "No flights found matching criteria",
                    "error"
                )
                return {
                    "status": "error",
                    "message": "No flights found for your search criteria",
                    "thoughts": self.thoughts
                }
            
            # Step 4: Let AI evaluate and select the best flight
            self._add_thought(
                f"Found {len(flights)} flights. Using AI to evaluate and select the best option",
                "evaluate_flights"
            )
            await asyncio.sleep(0.6)
            
            best_flight = await self.llm.select_best_flight([f.dict() for f in flights], search_params)
            
            # Find the selected flight object
            selected_flight = next((f for f in flights if f.flight_id == best_flight['flight_id']), flights[0])
            
            self._add_thought(
                f"AI selected: {selected_flight.airline} {selected_flight.flight_number} - {selected_flight.currency} {selected_flight.price}. Reason: {best_flight['reason']}",
                "flight_selected"
            )
            await asyncio.sleep(0.5)
            
            # Step 5: Proceed with booking
            self._add_thought(
                "Validating passenger details for booking",
                "validate_booking"
            )
            await asyncio.sleep(0.3)
            
            self._add_thought(
                f"Processing autonomous booking for flight {selected_flight.flight_id}",
                "process_booking"
            )
            await asyncio.sleep(0.5)
            
            booking_result = await self.flight_api.book_flight(selected_flight.flight_id, passenger_details)
            
            self._add_thought(
                f"Booking completed! Confirmation code: {booking_result.get('confirmation_code')}",
                "complete"
            )
            
            return {
                "status": "success",
                "search_id": search_id,
                "thoughts": self.thoughts,
                "selected_flight": selected_flight.dict(),
                "booking_result": booking_result,
                "all_flights": [f.dict() for f in flights],
                "selection_reason": best_flight['reason'],
                "message": f"Successfully booked {selected_flight.airline} {selected_flight.flight_number} for {selected_flight.currency} {selected_flight.price}"
            }
            
        except Exception as e:
            self._add_thought(
                f"Error occurred during autonomous booking: {str(e)}",
                "error"
            )
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}",
                "thoughts": self.thoughts
            }
    
    def _validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate search parameters"""
        if not params.get('origin'):
            return {"valid": False, "message": "Origin is required"}
        if not params.get('destination'):
            return {"valid": False, "message": "Destination is required"}
        if not params.get('departure_date'):
            return {"valid": False, "message": "Departure date is required"}
        
        # Add more validation as needed
        return {"valid": True, "message": "Parameters valid"}
    
    async def make_booking(self, flight_id: str, passenger_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a flight booking
        """
        self.thoughts = []
        
        self._add_thought(
            "Validating passenger details",
            "validate_booking"
        )
        await asyncio.sleep(0.3)
        
        self._add_thought(
            f"Processing booking for flight {flight_id}",
            "process_booking"
        )
        await asyncio.sleep(0.5)
        
        result = await self.flight_api.book_flight(flight_id, passenger_details)
        
        self._add_thought(
            "Booking completed successfully",
            "complete"
        )
        
        return result