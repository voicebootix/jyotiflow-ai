/**
 * Prokerala API Endpoints Configuration
 * Centralized configuration for astrology and numerology endpoints
 */

export const PROKERALA_ENDPOINTS = [
  '/astrology/birth-details',
  '/astrology/kundli/advanced', 
  '/astrology/planet-position',
  '/astrology/dasha-periods',
  '/astrology/yoga',
  '/astrology/nakshatra-porutham',
  '/astrology/kundli-matching',
  '/numerology/life-path-number',
  '/numerology/destiny-number',
  '/horoscope/daily',
  '/astrology/auspicious-period',
  '/astrology/birth-chart',
  '/astrology/chart'
];

export const ENDPOINT_CATEGORIES = {
  astrology: [
    '/astrology/birth-details',
    '/astrology/kundli/advanced',
    '/astrology/planet-position',
    '/astrology/dasha-periods',
    '/astrology/yoga',
    '/astrology/nakshatra-porutham',
    '/astrology/kundli-matching',
    '/astrology/auspicious-period',
    '/astrology/birth-chart',
    '/astrology/chart'
  ],
  numerology: [
    '/numerology/life-path-number',
    '/numerology/destiny-number'
  ],
  horoscope: [
    '/horoscope/daily'
  ]
};

export const getProkeralaEndpoints = () => {
  return PROKERALA_ENDPOINTS;
};

export const getEndpointsByCategory = (category) => {
  return ENDPOINT_CATEGORIES[category] || [];
};