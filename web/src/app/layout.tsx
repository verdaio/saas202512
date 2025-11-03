import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Pet Care Booking',
  description: 'Book grooming and training appointments for your pets',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
