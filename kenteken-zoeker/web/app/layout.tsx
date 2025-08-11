import './globals.css'

export const metadata = {
  title: 'Kenteken Zoeker',
  description: 'Openbare kenteken-zoeker',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="nl">
      <body className="min-h-screen antialiased">
        {children}
      </body>
    </html>
  )
}