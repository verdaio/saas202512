# Pet Care Booking - Frontend

Next.js 14 frontend with TypeScript and Tailwind CSS for the Pet Care booking system.

## Features

- **Booking Widget**: Complete 4-step booking flow
  - Step 1: Service selection
  - Step 2: Date and time selection
  - Step 3: Pet and owner information
  - Step 4: Confirmation

- **Responsive Design**: Mobile-first, works on all devices
- **Real-time Availability**: Fetches available time slots from API
- **Stripe Integration**: Ready for payment processing
- **SMS Notifications**: Auto-sends confirmations and reminders

## Getting Started

### Prerequisites

- Node.js 18+
- npm 9+
- Backend API running on port 5410

### Installation

```bash
cd web
npm install
```

### Environment Variables

Copy `.env.local` and configure:

```env
NEXT_PUBLIC_API_URL=http://localhost:5410
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
```

### Development

```bash
npm run dev
```

Open http://localhost:3010

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
web/
├── src/
│   ├── app/                    # Next.js 14 App Router
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   └── globals.css         # Global styles
│   ├── components/
│   │   ├── BookingWidget.tsx   # Main booking component
│   │   └── booking/            # Booking step components
│   │       ├── ServiceSelection.tsx
│   │       ├── DateTimeSelection.tsx
│   │       ├── PetOwnerForm.tsx
│   │       └── ConfirmationStep.tsx
│   └── lib/
│       └── api.ts              # API client
├── public/                     # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## API Integration

The frontend communicates with the backend API:

- **GET /api/v1/services** - List available services
- **GET /api/v1/appointments/availability/slots** - Get available time slots
- **POST /api/v1/appointments** - Create appointment
- **POST /api/v1/owners** - Create pet owner
- **POST /api/v1/pets** - Create pet

## Customization

### Branding

Update colors in `tailwind.config.js`:

```js
colors: {
  primary: {
    // Your brand colors
  }
}
```

### Templates

Booking widget templates are in `src/components/booking/`.

## Deployment

### Vercel (Recommended)

```bash
vercel --prod
```

### Docker

```bash
docker build -t pet-care-booking .
docker run -p 3010:3010 pet-care-booking
```

### Environment Variables for Production

```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_key_here
```

## Tech Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Date Handling**: date-fns
- **Payment**: Stripe

## Features Roadmap

- [x] Service selection
- [x] Date/time picker
- [x] Pet owner form
- [x] Confirmation screen
- [ ] Stripe payment integration (UI)
- [ ] Appointment management dashboard
- [ ] Email notifications
- [ ] Customer portal
- [ ] Admin dashboard

## License

Private - All rights reserved
