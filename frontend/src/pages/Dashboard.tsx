import { useState, useEffect } from 'react'
import { Grid, Card, Text, Title, Group, Badge, Select, Button } from '@mantine/core'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'
import { api } from '../utils/api'
import { Event, TargetOpportunity, Company } from '../types'

interface DashboardStats {
  new_incidents: Event[]
  top_opportunities: TargetOpportunity[]
  high_risk_subs: Company[]
  stats: {
    total_incidents_30d: number
    total_opportunities: number
    avg_propensity_score: number
  }
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeframe, setTimeframe] = useState('30')
  const [stateFilter, setStateFilter] = useState<string>('')

  useEffect(() => {
    fetchDashboardData()
  }, [timeframe, stateFilter])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      const since = new Date()
      since.setDate(since.getDate() - parseInt(timeframe))
      
      const [events, opportunities, companies] = await Promise.all([
        api.getEvents({ since: since.toISOString() }),
        api.getOpportunities({ min_score: 50, limit: 10 }),
        api.getCompanies({ type: 'Sub' })
      ])

      const highRiskSubs = companies.filter((company: Company) => {
        return events.some((event: Event) => event.company_id === company.id && event.severity_score > 60)
      })

      setData({
        new_incidents: events,
        top_opportunities: opportunities,
        high_risk_subs: highRiskSubs.slice(0, 10),
        stats: {
          total_incidents_30d: events.length,
          total_opportunities: opportunities.length,
          avg_propensity_score: opportunities.length > 0 
            ? opportunities.reduce((acc: number, opp: TargetOpportunity) => acc + opp.propensity_score, 0) / opportunities.length 
            : 0
        }
      })
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getIncidentTrendData = () => {
    if (!data) return []
    
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() - (6 - i))
      return {
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        incidents: data.new_incidents.filter(event => {
          const eventDate = new Date(event.occurred_on)
          return eventDate.toDateString() === date.toDateString()
        }).length
      }
    })
    
    return last7Days
  }

  const getSeverityDistribution = () => {
    if (!data) return []
    
    const ranges = [
      { name: 'Low (0-30)', min: 0, max: 30 },
      { name: 'Medium (31-60)', min: 31, max: 60 },
      { name: 'High (61-100)', min: 61, max: 100 }
    ]
    
    return ranges.map(range => ({
      name: range.name,
      count: data.new_incidents.filter(event => 
        event.severity_score >= range.min && event.severity_score <= range.max
      ).length
    }))
  }

  if (loading) {
    return <div>Loading dashboard...</div>
  }

  return (
    <div>
      <Group justify="space-between" mb="xl">
        <Title order={1}>Dashboard</Title>
        <Group>
          <Select
            placeholder="Timeframe"
            value={timeframe}
            onChange={(value) => setTimeframe(value || '30')}
            data={[
              { value: '7', label: 'Last 7 days' },
              { value: '30', label: 'Last 30 days' },
              { value: '90', label: 'Last 90 days' }
            ]}
            w={150}
          />
          <Button onClick={fetchDashboardData} variant="light">
            Refresh
          </Button>
        </Group>
      </Group>

      <Grid mb="xl">
        <Grid.Col span={4}>
          <Card padding="lg" radius="md" withBorder>
            <Group justify="space-between">
              <div>
                <Text c="dimmed" size="sm" weight={500} tt="uppercase">
                  New Incidents
                </Text>
                <Text weight={700} size="xl">
                  {data?.stats.total_incidents_30d || 0}
                </Text>
                <Text c="dimmed" size="xs">
                  Last {timeframe} days
                </Text>
              </div>
            </Group>
          </Card>
        </Grid.Col>

        <Grid.Col span={4}>
          <Card padding="lg" radius="md" withBorder>
            <Group justify="space-between">
              <div>
                <Text c="dimmed" size="sm" weight={500} tt="uppercase">
                  Target Opportunities
                </Text>
                <Text weight={700} size="xl">
                  {data?.stats.total_opportunities || 0}
                </Text>
                <Text c="dimmed" size="xs">
                  Score ≥ 50
                </Text>
              </div>
            </Group>
          </Card>
        </Grid.Col>

        <Grid.Col span={4}>
          <Card padding="lg" radius="md" withBorder>
            <Group justify="space-between">
              <div>
                <Text c="dimmed" size="sm" weight={500} tt="uppercase">
                  Avg Score
                </Text>
                <Text weight={700} size="xl">
                  {data?.stats.avg_propensity_score.toFixed(1) || 0}
                </Text>
                <Text c="dimmed" size="xs">
                  Propensity score
                </Text>
              </div>
            </Group>
          </Card>
        </Grid.Col>
      </Grid>

      <Grid>
        <Grid.Col span={6}>
          <Card padding="lg" radius="md" withBorder>
            <Title order={3} mb="md">Incident Trend</Title>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={getIncidentTrendData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="incidents" stroke="#228be6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Grid.Col>

        <Grid.Col span={6}>
          <Card padding="lg" radius="md" withBorder>
            <Title order={3} mb="md">Severity Distribution</Title>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={getSeverityDistribution()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#228be6" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Grid.Col>

        <Grid.Col span={6}>
          <Card padding="lg" radius="md" withBorder>
            <Title order={3} mb="md">Top Opportunities</Title>
            <div style={{ maxHeight: 300, overflowY: 'auto' }}>
              {data?.top_opportunities.map((opportunity) => (
                <Group key={opportunity.id} justify="space-between" mb="xs" p="xs" style={{ borderBottom: '1px solid #eee' }}>
                  <div>
                    <Text weight={600} size="sm">
                      {opportunity.gc?.name || opportunity.owner?.name || 'Unknown Company'}
                    </Text>
                    <Text size="xs" c="dimmed">
                      {opportunity.recommended_talk_track}
                    </Text>
                  </div>
                  <Badge color="orange" variant="light">
                    {opportunity.propensity_score.toFixed(0)}
                  </Badge>
                </Group>
              ))}
            </div>
          </Card>
        </Grid.Col>

        <Grid.Col span={6}>
          <Card padding="lg" radius="md" withBorder>
            <Title order={3} mb="md">High-Risk Subcontractors</Title>
            <div style={{ maxHeight: 300, overflowY: 'auto' }}>
              {data?.high_risk_subs.map((sub) => (
                <Group key={sub.id} justify="space-between" mb="xs" p="xs" style={{ borderBottom: '1px solid #eee' }}>
                  <div>
                    <Text weight={600} size="sm">{sub.name}</Text>
                    <Text size="xs" c="dimmed">{sub.state} • {sub.naics}</Text>
                  </div>
                  <Badge color="red" variant="light">
                    High Risk
                  </Badge>
                </Group>
              ))}
            </div>
          </Card>
        </Grid.Col>
      </Grid>
    </div>
  )
}