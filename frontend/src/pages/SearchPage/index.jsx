import React, { useState } from 'react';
import SearchForm from '../../components/SearchForm';
import AgentThinking from '../../components/AgentThinking';
import ResultsDisplay from '../../components/ResultsDisplay';
import { searchFlights, bookFlight, searchAndBookAutonomous } from '../../services/api';
import './index.scss';

const SearchPage = () => {
  const [loading, setLoading] = useState(false);
  const [autonomousLoading, setAutonomousLoading] = useState(false);
  const [searchResponse, setSearchResponse] = useState(null);
  const [autonomousBookingResponse, setAutonomousBookingResponse] = useState(null);
  const [bookingStatus, setBookingStatus] = useState(null);

  const handleSearch = async (searchParams) => {
    setLoading(true);
    setSearchResponse(null);
    setAutonomousBookingResponse(null);
    setBookingStatus(null);

    try {
      const response = await searchFlights(searchParams);
      setSearchResponse(response);
    } catch (error) {
      console.error('Search error:', error);
      alert('Error searching flights. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchAndBook = async (searchParams, passengerDetails) => {
    setAutonomousLoading(true);
    setSearchResponse(null);
    setAutonomousBookingResponse(null);
    setBookingStatus(null);

    try {
      const response = await searchAndBookAutonomous(searchParams, passengerDetails);
      setAutonomousBookingResponse(response);
      
      // Show success notification
      alert(`🎉 AI has successfully booked your flight!\n\nConfirmation Code: ${response.booking_result.confirmation_code}\n\nFlight: ${response.selected_flight.airline} ${response.selected_flight.flight_number}\n\nCheck your email for details!`);
    } catch (error) {
      console.error('Autonomous booking error:', error);
      alert('Error during autonomous booking. Please try again or use manual search.');
    } finally {
      setAutonomousLoading(false);
    }
  };

  const handleBook = async (bookingData) => {
    try {
      const response = await bookFlight(bookingData);
      setBookingStatus(response);
      alert(`Booking successful! Confirmation code: ${response.confirmation_code}`);
    } catch (error) {
      console.error('Booking error:', error);
      alert('Error booking flight. Please try again.');
    }
  };

  // Determine which thoughts to display
  const currentThoughts = autonomousBookingResponse?.thoughts || searchResponse?.thoughts || [];
  const isProcessing = loading || autonomousLoading;

  return (
    <div className="search-page">
      <div className="page-header">
        <h1>Find Your Perfect Flight</h1>
        <p>Our AI agent will search and analyze the best options for you</p>
      </div>

      <SearchForm 
        onSearch={handleSearch} 
        onSearchAndBook={handleSearchAndBook}
        loading={loading}
        autonomousLoading={autonomousLoading}
      />

      {(isProcessing || currentThoughts.length > 0) && (
        <AgentThinking 
          thoughts={currentThoughts} 
          isProcessing={isProcessing} 
        />
      )}

      {searchResponse && !loading && !autonomousLoading && (
        <ResultsDisplay 
          searchResponse={searchResponse} 
          onBook={handleBook} 
        />
      )}

      {autonomousBookingResponse && !autonomousLoading && (
        <ResultsDisplay 
          autonomousBookingResponse={autonomousBookingResponse}
        />
      )}

      {bookingStatus && !autonomousBookingResponse && (
        <div className="booking-success">
          <div className="success-icon">✅</div>
          <h3>Booking Confirmed!</h3>
          <p>Confirmation Code: <strong>{bookingStatus.confirmation_code}</strong></p>
          <p>{bookingStatus.message}</p>
        </div>
      )}
    </div>
  );
};

export default SearchPage;