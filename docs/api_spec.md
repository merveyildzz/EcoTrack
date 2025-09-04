# EcoTrack API Specification

## Overview
This document outlines the RESTful API endpoints for the EcoTrack application.

## Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://api.ecotrack.app/api/v1`

## Authentication
All protected endpoints require JWT authentication via the `Authorization` header:
```
Authorization: Bearer <jwt_token>
```

## Core Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login  
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - User logout

### Activities
- `GET /activities` - List user activities
- `POST /activities` - Create new activity
- `GET /activities/{id}` - Get specific activity
- `PUT /activities/{id}` - Update activity
- `DELETE /activities/{id}` - Delete activity

### Carbon Calculation
- `POST /calc` - Calculate carbon footprint for activity
- `GET /calc/factors` - Get emission factors
- `GET /calc/categories` - Get activity categories

### Dashboard
- `GET /dashboard` - Get dashboard data
- `GET /dashboard/summary` - Get summary metrics
- `GET /dashboard/trends` - Get trend analysis

### Leaderboards & Social
- `GET /leaderboard` - Get leaderboard data
- `GET /challenges` - List active challenges
- `POST /challenges/{id}/join` - Join a challenge

### AI Recommendations
- `POST /recommendations/daily` - Get daily recommendations
- `POST /products/search` - Search eco-friendly products

### User Profile
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `DELETE /profile` - Delete user account

## Data Models

### User
```json
{
  "id": "uuid",
  "email": "string",
  "created_at": "datetime",
  "timezone": "string",
  "settings": {
    "units": "metric|imperial",
    "privacy_level": "public|friends|private",
    "ai_recommendations": "boolean"
  }
}
```

### Activity
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "activity_type": "transportation|energy|food|consumption",
  "category": "string",
  "value": "number",
  "unit": "string",
  "start_timestamp": "datetime",
  "end_timestamp": "datetime",
  "location": {
    "type": "Point",
    "coordinates": [longitude, latitude]
  },
  "co2_kg": "number",
  "metadata": "object"
}
```

### Carbon Calculation
```json
{
  "co2_kg": "number",
  "breakdown": {
    "direct": "number",
    "indirect": "number",
    "scope_1": "number",
    "scope_2": "number",
    "scope_3": "number"
  },
  "factor_used": {
    "value": "number",
    "unit": "string",
    "source": "string",
    "version": "string"
  },
  "confidence": "high|medium|low"
}
```

## Response Formats

### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "string"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

## Rate Limits
- Authentication endpoints: 5 requests per minute
- Activity logging: 100 requests per hour
- AI recommendations: 50 requests per hour
- General API: 1000 requests per hour

## Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error