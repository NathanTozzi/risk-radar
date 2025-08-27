import { Routes, Route } from 'react-router-dom'
import { AppShell, Navbar, Header, Title, Group, Button, Text } from '@mantine/core'
import { Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import TargetList from './pages/TargetList'
import TargetDetail from './pages/TargetDetail'
import OutreachKit from './pages/OutreachKit'
import Admin from './pages/Admin'
import Search from './pages/Search'

function App() {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/targets', label: 'Target List' },
    { path: '/search', label: 'Search' },
    { path: '/admin', label: 'Admin' },
  ]

  return (
    <AppShell
      header={{ height: 70 }}
      navbar={{ width: 250, breakpoint: 'sm' }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Title order={2} c="blue">RiskRadar</Title>
            <Text size="sm" c="dimmed">BDR Intelligence Platform</Text>
          </Group>
          <Text size="xs" c="dimmed">
            Use public/regulatory data responsibly. Verify against official records.
          </Text>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Group direction="column" spacing="xs">
          {navItems.map((item) => (
            <Button
              key={item.path}
              component={Link}
              to={item.path}
              variant={location.pathname === item.path ? 'filled' : 'subtle'}
              fullWidth
              justify="left"
            >
              {item.label}
            </Button>
          ))}
        </Group>
      </AppShell.Navbar>

      <AppShell.Main>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/targets" element={<TargetList />} />
          <Route path="/targets/:id" element={<TargetDetail />} />
          <Route path="/outreach/:id" element={<OutreachKit />} />
          <Route path="/search" element={<Search />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </AppShell.Main>
    </AppShell>
  )
}

export default App