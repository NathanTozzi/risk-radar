import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  Title, 
  Card, 
  Text, 
  Group, 
  Badge, 
  Button, 
  Grid,
  Timeline,
  Progress,
  Table
} from '@mantine/core'
import { IconExternalLink, IconMail, IconFileText } from '@tabler/icons-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { api } from '../utils/api'
import { TargetOpportunity, Event, MetricsITA } from '../types'

export default function TargetDetail() {
  const { id } = useParams<{ id: string }>()
  const [opportunity, setOpportunity] = useState<TargetOpportunity | null>(null)
  const [events, setEvents] = useState<Event[]>([])
  const [itaMetrics, setItaMetrics] = useState<MetricsITA[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      fetchOpportunityDetail(parseInt(id))
    }
  }, [id])

  const fetchOpportunityDetail = async (opportunityId: number) => {
    try {
      setLoading(true)
      const opportunityData = await api.getOpportunity(opportunityId)
      setOpportunity(opportunityData)

      if (opportunityData.driver_event?.company_id) {
        const companyEvents = await api.getEvents({ 
          company_id: opportunityData.driver_event.company_id 
        })
        setEvents(companyEvents)
      }
      
    } catch (error) {
      console.error('Failed to fetch opportunity details:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateOutreachKit = async () => {
    if (!opportunity) return
    
    try {
      await api.generateOutreachKit(opportunity.id)
      // Navigate to outreach kit page
      window.location.href = `/outreach/${opportunity.id}`
    } catch (error) {
      console.error('Failed to generate outreach kit:', error)
    }
  }

  const getDartBenchmarkData = () => {
    if (!itaMetrics.length) return []
    
    // Mock benchmark data - in real app this would come from config
    const benchmarks = {
      'Construction': 4.2,
      'Roofing': 5.0,
      'Steel': 4.2
    }
    
    return itaMetrics.map(metric => ({
      year: metric.year,
      actual: metric.dart_rate || 0,
      benchmark: benchmarks['Construction'] || 4.2
    }))
  }

  const getEventsByType = () => {
    const types = ['inspection', 'citation', 'accident', 'news', 'ita']
    return types.map(type => ({
      type: type.charAt(0).toUpperCase() + type.slice(1),
      count: events.filter(event => event.event_type === type).length
    }))
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'accident': return '⚠️'
      case 'citation': return '📋'
      case 'inspection': return '🔍'
      case 'news': return '📰'
      case 'ita': return '📊'
      default: return '•'
    }
  }

  const getScoreBadgeColor = (score: number) => {
    if (score >= 80) return 'red'
    if (score >= 60) return 'orange'
    if (score >= 40) return 'yellow'
    return 'blue'
  }

  if (loading) {
    return <div>Loading target details...</div>
  }

  if (!opportunity) {
    return <div>Opportunity not found</div>
  }

  const company = opportunity.gc || opportunity.owner
  const companyType = opportunity.gc ? 'General Contractor' : 'Owner/Developer'

  return (
    <div>
      <Group justify="space-between" mb="lg">
        <div>
          <Title order={1}>{company?.name || 'Unknown Company'}</Title>
          <Text size="lg" c="dimmed">{companyType}</Text>
        </div>
        <Group>
          <Badge 
            size="xl" 
            color={getScoreBadgeColor(opportunity.propensity_score)}
            variant="filled"
          >
            Score: {opportunity.propensity_score.toFixed(0)}
          </Badge>
          <Button 
            onClick={generateOutreachKit}
            leftSection={<IconMail size={16} />}
          >
            Generate Outreach Kit
          </Button>
        </Group>
      </Group>

      <Grid>
        <Grid.Col span={8}>
          <Card padding="lg" radius="md" withBorder mb="lg">
            <Title order={3} mb="md">Company Profile</Title>
            <Table>
              <Table.Tbody>
                <Table.Tr>
                  <Table.Td width={150}><strong>Name</strong></Table.Td>
                  <Table.Td>{company?.name}</Table.Td>
                </Table.Tr>
                <Table.Tr>
                  <Table.Td><strong>Type</strong></Table.Td>
                  <Table.Td>{companyType}</Table.Td>
                </Table.Tr>
                <Table.Tr>
                  <Table.Td><strong>State</strong></Table.Td>
                  <Table.Td>{company?.state || 'N/A'}</Table.Td>
                </Table.Tr>
                <Table.Tr>
                  <Table.Td><strong>NAICS</strong></Table.Td>
                  <Table.Td>{company?.naics || 'N/A'}</Table.Td>
                </Table.Tr>
                <Table.Tr>
                  <Table.Td><strong>Website</strong></Table.Td>
                  <Table.Td>
                    {company?.website ? (
                      <Group>
                        <Text>{company.website}</Text>
                        <Button 
                          size="xs" 
                          variant="light" 
                          component="a" 
                          href={company.website} 
                          target="_blank"
                          rightSection={<IconExternalLink size={12} />}
                        >
                          Visit
                        </Button>
                      </Group>
                    ) : 'N/A'}
                  </Table.Td>
                </Table.Tr>
                <Table.Tr>
                  <Table.Td><strong>Talk Track</strong></Table.Td>
                  <Table.Td>
                    <Badge variant="light">{opportunity.recommended_talk_track}</Badge>
                  </Table.Td>
                </Table.Tr>
              </Table.Tbody>
            </Table>
          </Card>

          <Card padding="lg" radius="md" withBorder mb="lg">
            <Title order={3} mb="md">Incident Timeline</Title>
            <Timeline active={events.length} bulletSize={24} lineWidth={2}>
              {events
                .sort((a, b) => new Date(b.occurred_on).getTime() - new Date(a.occurred_on).getTime())
                .slice(0, 10)
                .map((event) => (
                  <Timeline.Item
                    key={event.id}
                    bullet={getEventIcon(event.event_type)}
                    title={
                      <Group>
                        <Text weight={600} size="sm">
                          {event.event_type.charAt(0).toUpperCase() + event.event_type.slice(1)}
                        </Text>
                        <Badge size="sm" color={event.severity_score > 50 ? 'red' : 'yellow'}>
                          {event.severity_score.toFixed(0)}
                        </Badge>
                      </Group>
                    }
                  >
                    <Text c="dimmed" size="xs">
                      {formatDate(event.occurred_on)}
                    </Text>
                    <Text size="sm" mt="xs">
                      {event.data.narrative || event.data.title || `${event.event_type} event`}
                    </Text>
                    {event.link && (
                      <Button 
                        size="xs" 
                        variant="subtle" 
                        mt="xs"
                        component="a" 
                        href={event.link} 
                        target="_blank"
                        rightSection={<IconExternalLink size={12} />}
                      >
                        View Details
                      </Button>
                    )}
                  </Timeline.Item>
                ))}
            </Timeline>
          </Card>
        </Grid.Col>

        <Grid.Col span={4}>
          <Card padding="lg" radius="md" withBorder mb="lg">
            <Title order={3} mb="md">Propensity Breakdown</Title>
            <div>
              <Group justify="space-between" mb="xs">
                <Text size="sm">Incident Recency</Text>
                <Text size="sm" weight={600}>30/30</Text>
              </Group>
              <Progress value={100} size="sm" mb="md" color="red" />
              
              <Group justify="space-between" mb="xs">
                <Text size="sm">Severity Score</Text>
                <Text size="sm" weight={600}>25/25</Text>
              </Group>
              <Progress value={100} size="sm" mb="md" color="orange" />
              
              <Group justify="space-between" mb="xs">
                <Text size="sm">Frequency</Text>
                <Text size="sm" weight={600}>10/15</Text>
              </Group>
              <Progress value={67} size="sm" mb="md" color="yellow" />
              
              <Group justify="space-between" mb="xs">
                <Text size="sm">Trade Risk</Text>
                <Text size="sm" weight={600}>5/5</Text>
              </Group>
              <Progress value={100} size="sm" mb="md" color="blue" />
              
              <Group justify="space-between" mb="xs">
                <Text size="sm">Relationship</Text>
                <Text size="sm" weight={600}>4/5</Text>
              </Group>
              <Progress value={80} size="sm" color="teal" />
            </div>
          </Card>

          <Card padding="lg" radius="md" withBorder mb="lg">
            <Title order={3} mb="md">Event Distribution</Title>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={getEventsByType()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#228be6" />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {getDartBenchmarkData().length > 0 && (
            <Card padding="lg" radius="md" withBorder>
              <Title order={3} mb="md">DART vs Benchmark</Title>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={getDartBenchmarkData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="actual" fill="#e03131" name="Actual" />
                  <Bar dataKey="benchmark" fill="#228be6" name="Benchmark" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          )}
        </Grid.Col>
      </Grid>
    </div>
  )
}