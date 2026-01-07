import ollama
from typing import Dict, Any, List
from app.config import get_settings
import json
import re

settings = get_settings()

class LLMClient:
    def __init__(self):
        self.model = settings.ollama_model
        self.host = settings.ollama_host
    
    async def generate_response(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        """
        Generate a response from the LLM
        """
        try:
            messages = context or []
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = ollama.chat(
                model=self.model,
                messages=messages
            )
            
            return response['message']['content']
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return f"Error: {str(e)}"
    
    async def analyze_search_intent(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the user's search intent and determine the best approach
        """
        prompt = f"""
        Analyze this flight search request and provide insights:
        
        Origin: {search_params.get('origin')}
        Destination: {search_params.get('destination')}
        Departure Date: {search_params.get('departure_date')}
        Return Date: {search_params.get('return_date', 'N/A')}
        Passengers: {search_params.get('passengers')}
        Trip Type: {search_params.get('trip_type')}
        Cabin Class: {search_params.get('cabin_class')}
        
        Provide a brief analysis in 2-3 sentences about:
        1. The search parameters
        2. What to look for in the results
        
        Keep it concise and helpful.
        """
        
        response = await self.generate_response(prompt)
        
        return {
            "analysis": response,
            "search_strategy": "price_focused" if search_params.get('cabin_class') == 'economy' else "comfort_focused"
        }
    
    async def select_best_flight(self, flights: List[Dict[str, Any]], search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to select the best flight from available options
        """
        # Prepare flight summary for LLM
        flight_summaries = []
        for i, flight in enumerate(flights[:10]):  # Limit to top 10 to avoid token limits
            flight_summaries.append(
                f"Flight {i+1}: {flight['airline']} {flight['flight_number']} - "
                f"Price: {flight['currency']} {flight['price']}, "
                f"Duration: {flight['duration']}, "
                f"Stops: {flight['stops']}, "
                f"Departure: {flight['departure_time'].split('T')[1][:5]}, "
                f"ID: {flight['flight_id']}"
            )
        
        cabin_class = search_params.get('cabin_class', 'economy')
        
        prompt = f"""
        You are a travel booking AI agent. Select the BEST flight from these options for the user.
        
        User preferences:
        - Cabin Class: {cabin_class}
        - Passengers: {search_params.get('passengers', 1)}
        
        Available flights:
        {chr(10).join(flight_summaries)}
        
        Selection criteria priority:
        1. For economy class: Best value (balance of price and convenience)
        2. For business/first: Comfort and convenience over price
        3. Prefer non-stop or fewer stops
        4. Prefer reasonable departure times
        
        Respond ONLY in this exact format:
        FLIGHT_ID: [the flight_id]
        REASON: [one sentence explaining why this is the best choice]
        
        Example:
        FLIGHT_ID: FL1234
        REASON: Best value with non-stop service at a competitive price.
        """
        
        response = await self.generate_response(prompt)
        
        # Parse the response
        flight_id_match = re.search(r'FLIGHT_ID:\s*(\S+)', response)
        reason_match = re.search(r'REASON:\s*(.+?)(?:\n|$)', response, re.DOTALL)
        
        if flight_id_match:
            flight_id = flight_id_match.group(1).strip()
            reason = reason_match.group(1).strip() if reason_match else "Selected as the best overall option"
        else:
            # Fallback: select the first flight (best price since they're sorted)
            flight_id = flights[0]['flight_id']
            reason = "Selected based on best price and value"
        
        return {
            "flight_id": flight_id,
            "reason": reason
        }
    
    async def make_decision(self, situation: str, options: List[str]) -> str:
        """
        Make a decision based on the given situation and options
        """
        prompt = f"""
        Situation: {situation}
        
        Available options:
        {chr(10).join(f"{i+1}. {opt}" for i, opt in enumerate(options))}
        
        Choose the best option and explain why in one sentence.
        Format: "Option X because [reason]"
        """
        
        response = await self.generate_response(prompt)
        return response
    
    async def generate_search_summary(self, flights: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of the search results
        """
        if not flights:
            return "No flights found matching your criteria."
        
        prompt = f"""
        Summarize these flight search results in 2-3 sentences:
        
        Total flights found: {len(flights)}
        Price range: ${min(f.get('price', 0) for f in flights)} - ${max(f.get('price', 0) for f in flights)}
        Airlines: {', '.join(set(f.get('airline', 'Unknown') for f in flights[:5]))}
        
        Provide a helpful summary for the user.
        """
        
        response = await self.generate_response(prompt)
        return response