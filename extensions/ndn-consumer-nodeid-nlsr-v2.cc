/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2013 GTA, UFRJ, RJ - Brasil
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Author: João Vitor Torres <jvitor@gta.ufrj.br>
 */
 
 //ConsumerNodeIDNLSRV2 modifies ConsuConsumerBase
 //ConsumerNodeIDNLSRV2 keeps a constant number of pending insterests.
 //It is used to:
 //- monitor connectivity with neighbors
 //- exchange LSDB hashes and allow database synchronization
 

#include "ns3/log.h"
#include "ndn-consumer-nodeid-nlsr-v2.h"
#include <ns3/ndnSIM/model/fib/ndn-fib.h>
#include <ns3/ndnSIM/model/ndn-l3-protocol.h>
#include <ns3/ndnSIM/model/ndn-data.h>
#include "best-route-nlsr-v2.h"
#include "ns3/ndnSIM/utils/ndn-fw-hop-count-tag.h"
#include "ns3/ndn-interest.h"

NS_LOG_COMPONENT_DEFINE ("ndn.ConsumerNodeIDNLSRV2");

namespace ns3 {
namespace ndn {
    
NS_OBJECT_ENSURE_REGISTERED (ConsumerNodeIDNLSRV2);
 
   
TypeId
ConsumerNodeIDNLSRV2::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::ndn::ConsumerNodeIDNLSRV2")
    .SetGroupName ("Ndn")
    .SetParent<ConsumerBase> ()
    .AddConstructor<ConsumerNodeIDNLSRV2> ()
    ;

  return tid;
}

// Application Methods
void
ConsumerNodeIDNLSRV2::StartApplication () // Called at time specified by Start
{
// Interest : /hello/nodeid/roothash/seq
  NS_LOG_FUNCTION_NOARGS ();
  m_interestName = Name ("/hello");
  m_interestName.appendSeqNum (GetNode()->GetId());
  NS_LOG_INFO("Name: " << m_interestName);
  m_interestLifeTime = Seconds (1.0 / m_frequency);
  Ptr<L3Protocol> ndn = GetNode()->GetObject<L3Protocol> ();
  for (u_int32_t faces = 0; faces < GetNode()->GetNDevices (); faces++)
  {
    (GetNode()->GetObject<ns3::ndn::fw::BestRouteNLSRV2> ())
      ->AddFibEntry (m_interestName, ndn->GetFaceByNetDevice(GetNode()->GetDevice (faces)), 0);  		
  }
  (GetNode()->GetObject<ns3::ndn::fw::BestRouteNLSRV2> ())->SetNewNeighbor (true);
  // do base stuff
  ConsumerBase::StartApplication ();
}


void
ConsumerNodeIDNLSRV2::ScheduleNextPacket ()
{
  Ptr<L3Protocol>     ndn = GetNode()->GetObject<L3Protocol> ();
  for (u_int32_t faces = 0; faces < GetNode()->GetNDevices (); faces++)
  {
    (GetNode()->GetObject<ns3::ndn::fw::BestRouteNLSRV2> ())
      ->AddFibEntry (m_interestName.getPrefix(2), ndn->GetFaceByNetDevice(GetNode()->GetDevice (faces)), 0);  	
  }
  UpdateInterest ();
  Simulator::Schedule (Seconds(1.0 / (1.1 * m_frequency)),
                                       &ConsumerNodeIDNLSRV2::UpdateInterest, this);
  ConsumerBase::ScheduleNextPacket();
}

void
ConsumerNodeIDNLSRV2::UpdateInterest ()
{
  m_interestName = Name ("/hello");
  m_interestName.appendSeqNum (GetNode()->GetId());
  uint32_t roothash = 
    (GetNode()->GetObject<ns3::ndn::fw::BestRouteNLSRV2> ())->GetRootHash();
  NS_LOG_DEBUG ("Number before: " << roothash);
  m_interestName.appendSeqNum (roothash);
  NS_LOG_DEBUG ("Node (" << GetNode()->GetId() << ") Interest without seq: " << m_interestName.toUri());
}

///////////////////////////////////////////////////
//          Process incoming packets             //
///////////////////////////////////////////////////

void
ConsumerNodeIDNLSRV2::OnData (Ptr<const Data> contentObject)
{
  NS_LOG_DEBUG("Received Hello content " << contentObject->GetName() );
  ConsumerBase::OnData (contentObject); // tracing inside  
  ScheduleNextPacket ();
}

void
ConsumerNodeIDNLSRV2::OnTimeout (uint32_t sequenceNumber)
{
  NS_LOG_DEBUG("Seq timeout! " << sequenceNumber);
  ConsumerBase::OnTimeout (sequenceNumber);
}


} // namespace ndn
} // namespace ns3
