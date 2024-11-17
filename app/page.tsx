'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { toast } from "@/components/ui/use-toast"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Switch } from "@/components/ui/switch"

export default function LicenseManager() {
  const [licenses, setLicenses] = useState([])
  const [newLicense, setNewLicense] = useState({
    key: '',
    days: 0,
    hours: 0,
    subscription_type: '1 Week',
    support_name: '',
    key_type: 'restricted',
    multi_device: false
  })
  const [resetKey, setResetKey] = useState('')
  const [activationKey, setActivationKey] = useState('')
  const [deviceId, setDeviceId] = useState('')

  useEffect(() => {
    fetchLicenses()
  }, [])

  const fetchLicenses = async () => {
    try {
      const response = await fetch('/api/licenses')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setLicenses(data)
    } catch (error) {
      console.error("Error fetching licenses:", error)
      toast({
        title: "Error",
        description: "Failed to fetch licenses. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleAddLicense = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/add_license', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newLicense)
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      await fetchLicenses()
      setNewLicense({
        key: '',
        days: 0,
        hours: 0,
        subscription_type: '1 Week',
        support_name: '',
        key_type: 'restricted',
        multi_device: false
      })
      toast({
        title: "Success",
        description: "License added successfully.",
      })
    } catch (error) {
      console.error("Error adding license:", error)
      toast({
        title: "Error",
        description: "Failed to add license. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleToggleActive = async (id: number) => {
    try {
      const response = await fetch(`/api/toggle_active/${id}`, { method: 'POST' })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      await fetchLicenses()
      toast({
        title: "Success",
        description: "License status toggled successfully.",
      })
    } catch (error) {
      console.error("Error toggling license:", error)
      toast({
        title: "Error",
        description: "Failed to toggle license status. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleDeleteLicense = async (id: number) => {
    if (confirm('Are you sure you want to delete this license?')) {
      try {
        const response = await fetch(`/api/delete_license/${id}`, { method: 'DELETE' })
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        await fetchLicenses()
        toast({
          title: "Success",
          description: "License deleted successfully.",
        })
      } catch (error) {
        console.error("Error deleting license:", error)
        toast({
          title: "Error",
          description: "Failed to delete license. Please try again.",
          variant: "destructive",
        })
      }
    }
  }

  const handleResetKey = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/reset_key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: resetKey })
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      await fetchLicenses()
      setResetKey('')
      toast({
        title: "Success",
        description: "Key reset successfully.",
      })
    } catch (error) {
      console.error("Error resetting key:", error)
      toast({
        title: "Error",
        description: "Failed to reset key. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleActivateKey = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      console.log('Sending activation request:', { key: activationKey, device_id: deviceId })
      const response = await fetch('/api/check_key_details', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: activationKey, device_id: deviceId })
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      console.log('Activation response:', data)
      if (data.valid) {
        toast({
          title: "Success",
          description: `Key activated successfully. Expires on ${data.expiration_date}`,
        })
      } else {
        toast({
          title: "Error",
          description: data.reason,
          variant: "destructive",
        })
      }
      setActivationKey('')
      setDeviceId('')
    } catch (error) {
      console.error("Error activating key:", error)
      toast({
        title: "Error",
        description: "Failed to activate key. Please try again.",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="min-h-screen bg-black text-white p-4 space-y-8">
      <header className="text-center">
        <h1 className="text-5xl font-bold text-red-600 mb-2">MAGIC TRADING</h1>
        <p className="text-xl text-gray-400">License Management System</p>
      </header>

      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-2xl text-red-500">License List</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-gray-400">ID</TableHead>
                  <TableHead className="text-gray-400">Key</TableHead>
                  <TableHead className="text-gray-400">Active</TableHead>
                  <TableHead className="text-gray-400">Expiration Date</TableHead>
                  <TableHead className="text-gray-400">Subscription Type</TableHead>
                  <TableHead className="text-gray-400">Support Name</TableHead>
                  <TableHead className="text-gray-400">Device ID</TableHead>
                  <TableHead className="text-gray-400">Activated</TableHead>
                  <TableHead className="text-gray-400">Key Type</TableHead>
                  <TableHead className="text-gray-400">Multi-Device</TableHead>
                  <TableHead className="text-gray-400">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {licenses.map((license) => (
                  <TableRow key={license.id} className="border-gray-700">
                    <TableCell>{license.id}</TableCell>
                    <TableCell>{license.key}</TableCell>
                    <TableCell>{license.active ? 'Yes' : 'No'}</TableCell>
                    <TableCell>{new Date(license.expiration_date).toLocaleDateString()}</TableCell>
                    <TableCell>{license.subscription_type}</TableCell>
                    <TableCell>{license.support_name || 'N/A'}</TableCell>
                    <TableCell>{license.device_id || 'N/A'}</TableCell>
                    <TableCell>{license.activated ? 'Yes' : 'No'}</TableCell>
                    <TableCell>{license.key_type}</TableCell>
                    <TableCell>{license.multi_device ? 'Yes' : 'No'}</TableCell>
                    <TableCell>
                      <div className="space-x-2">
                        <Button onClick={() => handleToggleActive(license.id)} variant="outline" size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
                          {license.active ? 'Deactivate' : 'Activate'}
                        </Button>
                        <Button onClick={() => handleDeleteLicense(license.id)} variant="destructive" size="sm" className="bg-red-600 hover:bg-red-700">
                          Delete
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="add-key" className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-gray-800">
          <TabsTrigger value="add-key" className="text-gray-300 data-[state=active]:bg-gray-700">Add New Key</TabsTrigger>
          <TabsTrigger value="reset-key" className="text-gray-300 data-[state=active]:bg-gray-700">Reset Key</TabsTrigger>
          <TabsTrigger value="activate-key" className="text-gray-300 data-[state=active]:bg-gray-700">Activate Key</TabsTrigger>
        </TabsList>
        <TabsContent value="add-key">
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-2xl text-red-500">Add New Key</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAddLicense} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="key" className="text-gray-300">Key</Label>
                    <Input
                      id="key"
                      value={newLicense.key}
                      onChange={(e) => setNewLicense({ ...newLicense, key: e.target.value })}
                      required
                      className="bg-gray-800 text-white border-gray-700"
                    />
                  </div>
                  <div>
                    <Label htmlFor="days" className="text-gray-300">Duration (Days)</Label>
                    <Input
                      id="days"
                      type="number"
                      value={newLicense.days}
                      onChange={(e) => setNewLicense({ ...newLicense, days: parseInt(e.target.value) })}
                      min="0"
                      className="bg-gray-800 text-white border-gray-700"
                    />
                  </div>
                  <div>
                    <Label htmlFor="hours" className="text-gray-300">Duration (Hours)</Label>
                    <Input
                      id="hours"
                      type="number"
                      value={newLicense.hours}
                      onChange={(e) => setNewLicense({ ...newLicense, hours: parseInt(e.target.value) })}
                      min="0"
                      className="bg-gray-800 text-white border-gray-700"
                    />
                  </div>
                  <div>
                    <Label htmlFor="subscription_type" className="text-gray-300">Subscription Type</Label>
                    <Select
                      value={newLicense.subscription_type}
                      onValueChange={(value) => setNewLicense({ ...newLicense, subscription_type: value })}
                    >
                      <SelectTrigger className="bg-gray-800 text-white border-gray-700">
                        <SelectValue placeholder="Select subscription type" />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-800 text-white border-gray-700">
                        <SelectItem value="1 Week">1 Week</SelectItem>
                        <SelectItem value="1 Month">1 Month</SelectItem>
                        <SelectItem value="3 Months">3 Months</SelectItem>
                        <SelectItem value="6 Months">6 Months</SelectItem>
                        <SelectItem value="1 Year">1 Year</SelectItem>
                        <SelectItem value="Free Trial">Free Trial</SelectItem>
                        <SelectItem value="Hours">Hours</SelectItem>
                        <SelectItem value="Days">Days</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="support_name" className="text-gray-300">Support Name (optional)</Label>
                    <Input
                      id="support_name"
                      value={newLicense.support_name}
                      onChange={(e) => setNewLicense({ ...newLicense, support_name: e.target.value })}
                      className="bg-gray-800 text-white border-gray-700"
                    />
                  </div>
                  <div>
                    <Label htmlFor="key_type" className="text-gray-300">Key Type</Label>
                    <Select
                      value={newLicense.key_type}
                      onValueChange={(value) => setNewLicense({ ...newLicense, key_type: value })}
                    >
                      <SelectTrigger className="bg-gray-800 text-white border-gray-700">
                        <SelectValue placeholder="Select key type" />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-800 text-white border-gray-700">
                        <SelectItem value="restricted">Restricted</SelectItem>
                        <SelectItem value="unrestricted">Unrestricted</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="multi_device"
                      checked={newLicense.multi_device}
                      onCheckedChange={(checked) => setNewLicense({ ...newLicense, multi_device: checked })}
                    />
                    <Label htmlFor="multi_device" className="text-gray-300">Multi-Device Key</Label>
                  </div>
                </div>
                <Button type="submit" className="w-full bg-red-600 hover:bg-red-700 text-white">Add Key</Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="reset-key">
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-2xl text-red-500">Reset Key</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleResetKey} className="space-y-4">
                <div>
                  <Label htmlFor="reset_key" className="text-gray-300">Key</Label>
                  <Input
                    id="reset_key"
                    value={resetKey}
                    onChange={(e) => setResetKey(e.target.value)}
                    required
                    className="bg-gray-800 text-white border-gray-700"
                  />
                </div>
                <Button type="submit" className="w-full bg-yellow-600 hover:bg-yellow-700 text-white">Reset Key</Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="activate-key">
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-2xl text-red-500">Activate Key</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleActivateKey} className="space-y-4">
                <div>
                  <Label htmlFor="activation_key" className="text-gray-300">Activation Key</Label>
                  <Input
                    id="activation_key"
                    value={activationKey}
                    onChange={(e) => setActivationKey(e.target.value)}
                    required
                    className="bg-gray-800 text-white border-gray-700"
                  />
                </div>
                <div>
                  <Label htmlFor="device_id" className="text-gray-300">Device ID</Label>
                  <Input
                    id="device_id"
                    value={deviceId}
                    onChange={(e) => setDeviceId(e.target.value)}
                    required
                    className="bg-gray-800 text-white border-gray-700"
                  />
                </div>
                <Button type="submit" className="w-full bg-green-600 hover:bg-green-700 text-white">Activate Key</Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <footer className="text-center text-gray-400">
        <p className="font-bold text-xl"># MAGIC TRADING #</p>
        <p className="text-lg">LETS LIFE SURPRISE YOU</p>
      </footer>
    </div>
  )
}
