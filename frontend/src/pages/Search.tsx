import { useState } from 'react'
import { 
  TextInput, 
  Button, 
  Card, 
  Title, 
  Group, 
  Table,
  Badge,
  Text,
  Select,
  Tabs
} from '@mantine/core'
import { IconSearch } from '@tabler/icons-react'
import { Link } from 'react-router-dom'
import { api } from '../utils/api'
import { Company, Event } from '../types'

export default function Search() {
  const [searchTerm, setSearchTerm] = useState('')
  const [searchType, setSearchType] = useState('all')
  const [companies, setCompanies] = useState<Company[]>([])
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(false)

  const handleSearch = async () => {
    if (!searchTerm.trim()) return

    try {
      setLoading(true)
      
      if (searchType === 'companies' || searchType === 'all') {
        const companyResults = await api.getCompanies({ q: searchTerm })
        setCompanies(companyResults)
      }
      
      if (searchType === 'events' || searchType === 'all') {
        const eventResults = await api.getEvents({})
        const filteredEvents = eventResults.filter((event: Event) =>
          JSON.stringify(event.data).toLowerCase().includes(searchTerm.toLowerCase()) ||
          event.source.toLowerCase().includes(searchTerm.toLowerCase())
        )
        setEvents(filteredEvents)
      }
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const getEventBadgeColor = (eventType: string) => {
    switch (eventType) {
      case 'accident': return 'red'
      case 'citation': return 'orange'
      case 'inspection': return 'yellow'
      case 'news': return 'blue'
      default: return 'gray'
    }
  }

  return (
    <div>
      <Title order={1} mb="lg">Universal Search</Title>

      <Card padding="lg" radius="md" withBorder mb="lg">
        <Group mb="md">
          <TextInput
            placeholder="Search companies, events, projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.currentTarget.value)}
            leftSection={<IconSearch size={16} />}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            style={{ flex: 1 }}
          />
          <Select
            value={searchType}
            onChange={(value) => setSearchType(value || 'all')}
            data={[
              { value: 'all', label: 'All' },
              { value: 'companies', label: 'Companies' },
              { value: 'events', label: 'Events' }
            ]}
            w={120}
          />
          <Button onClick={handleSearch} loading={loading}>
            Search
          </Button>
        </Group>
      </Card>

      {(companies.length > 0 || events.length > 0) && (
        <Tabs defaultValue="companies">
          <Tabs.List mb="lg">
            <Tabs.Tab value="companies">
              Companies ({companies.length})
            </Tabs.Tab>
            <Tabs.Tab value="events">
              Events ({events.length})
            </Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value="companies">
            <Card padding="lg" radius="md" withBorder>
              <Table>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Name</Table.Th>
                    <Table.Th>Type</Table.Th>
                    <Table.Th>State</Table.Th>
                    <Table.Th>NAICS</Table.Th>
                    <Table.Th>Actions</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {companies.map((company) => (
                    <Table.Tr key={company.id}>
                      <Table.Td>
                        <Text weight={600}>{company.name}</Text>
                      </Table.Td>
                      <Table.Td>
                        <Badge variant="light">{company.type}</Badge>
                      </Table.Td>
                      <Table.Td>{company.state || 'N/A'}</Table.Td>
                      <Table.Td>{company.naics || 'N/A'}</Table.Td>
                      <Table.Td>
                        <Button size="xs" variant="light" component={Link} to={`/companies/${company.id}`}>
                          View
                        </Button>
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            </Card>
          </Tabs.Panel>

          <Tabs.Panel value="events">
            <Card padding="lg" radius="md" withBorder>
              <Table>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Event</Table.Th>
                    <Table.Th>Company</Table.Th>
                    <Table.Th>Date</Table.Th>
                    <Table.Th>Severity</Table.Th>
                    <Table.Th>Source</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {events.map((event) => (
                    <Table.Tr key={event.id}>
                      <Table.Td>
                        <Group>
                          <Badge 
                            variant="filled" 
                            color={getEventBadgeColor(event.event_type)}
                            size="sm"
                          >
                            {event.event_type}
                          </Badge>
                          <Text size="sm">
                            {event.data.title || event.data.narrative || 'Event'}
                          </Text>
                        </Group>
                      </Table.Td>
                      <Table.Td>
                        <Text size="sm">{event.company?.name || `Company ${event.company_id}`}</Text>
                      </Table.Td>
                      <Table.Td>
                        <Text size="sm">{formatDate(event.occurred_on)}</Text>
                      </Table.Td>
                      <Table.Td>
                        <Badge 
                          variant="light" 
                          color={event.severity_score > 50 ? 'red' : 'yellow'}
                        >
                          {event.severity_score.toFixed(0)}
                        </Badge>
                      </Table.Td>
                      <Table.Td>
                        <Text size="xs" c="dimmed">{event.source}</Text>
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            </Card>
          </Tabs.Panel>
        </Tabs>
      )}

      {!loading && companies.length === 0 && events.length === 0 && searchTerm && (
        <Card padding="lg" radius="md" withBorder>
          <Text c="dimmed" ta="center">
            No results found for "{searchTerm}". Try different search terms or check spelling.
          </Text>
        </Card>
      )}
    </div>
  )
}