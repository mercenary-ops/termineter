#  termineter/modules/get_identification.py
#
#  Copyright 2017 Spencer J. McIntyre <SMcIntyre [at] SecureState [dot] net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

from __future__ import unicode_literals

import c1218.data
from termineter.module import TermineterModuleOptical

class Module(TermineterModuleOptical):
	connection_state = TermineterModuleOptical.connection_states.none
	def __init__(self, *args, **kwargs):
		TermineterModuleOptical.__init__(self, *args, **kwargs)
		self.author = ['Spencer McIntyre']
		self.description = 'Read And Parse The Identification Information'
		self.detailed_description = 'This module reads and parses the information from the C12.18 identification service.'

	def run(self):
		conn = self.frmwk.serial_connection
		conn.send(c1218.data.C1218IdentRequest())
		resp = c1218.data.C1218Packet(conn.recv())

		self.frmwk.print_status('Received Identity Response:')
		self.frmwk.print_hexdump(resp.data)

		if resp.data[0] != c1218.data.C1218_RESPONSE_CODES['ok']:
			self.frmwk.print_error("Non-ok response status 0x{0} ({1}) received".format(
				resp.data[0],
				c1218.data.C1218_RESPONSE_CODES.get(resp.data[0], 'unknown response code')
			))
		if len(resp.data) < 5:
			self.frmwk.print_error('Received less that the expected amount of data')
			return
		standard, ver, rev = resp.data[1:4]
		standard = {
			0: 'ANSI C12.18',
			1: 'Reserved',
			2: 'ANSI C12.21',
			3: 'ANSI C12.22'
		}.get(standard, "Unknown (0x{0:02x})".format(standard))
		rows = [
			('Reference Standard', standard),
			('Standard Version', "{0}.{1}".format(ver, rev))
		]
		cursor = 4
		if resp.data[cursor] == 0:
			rows.append(('Feature', 'N/A'))
		# the feature list is null terminated as defined in the c12.18 standard
		self.frmwk.print_table(rows, headers=('Name', 'Value'))
