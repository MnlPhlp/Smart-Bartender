# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: bartender.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='bartender.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0f\x62\x61rtender.proto\"\x1d\n\x0c\x44rinkRequest\x12\r\n\x05\x64rink\x18\x01 \x01(\t\"1\n\rDrinkResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t27\n\tBartender\x12*\n\tMakeDrink\x12\r.DrinkRequest\x1a\x0e.DrinkResponseb\x06proto3'
)




_DRINKREQUEST = _descriptor.Descriptor(
  name='DrinkRequest',
  full_name='DrinkRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='drink', full_name='DrinkRequest.drink', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=19,
  serialized_end=48,
)


_DRINKRESPONSE = _descriptor.Descriptor(
  name='DrinkResponse',
  full_name='DrinkResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='success', full_name='DrinkResponse.success', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='message', full_name='DrinkResponse.message', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=50,
  serialized_end=99,
)

DESCRIPTOR.message_types_by_name['DrinkRequest'] = _DRINKREQUEST
DESCRIPTOR.message_types_by_name['DrinkResponse'] = _DRINKRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DrinkRequest = _reflection.GeneratedProtocolMessageType('DrinkRequest', (_message.Message,), {
  'DESCRIPTOR' : _DRINKREQUEST,
  '__module__' : 'bartender_pb2'
  # @@protoc_insertion_point(class_scope:DrinkRequest)
  })
_sym_db.RegisterMessage(DrinkRequest)

DrinkResponse = _reflection.GeneratedProtocolMessageType('DrinkResponse', (_message.Message,), {
  'DESCRIPTOR' : _DRINKRESPONSE,
  '__module__' : 'bartender_pb2'
  # @@protoc_insertion_point(class_scope:DrinkResponse)
  })
_sym_db.RegisterMessage(DrinkResponse)



_BARTENDER = _descriptor.ServiceDescriptor(
  name='Bartender',
  full_name='Bartender',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=101,
  serialized_end=156,
  methods=[
  _descriptor.MethodDescriptor(
    name='MakeDrink',
    full_name='Bartender.MakeDrink',
    index=0,
    containing_service=None,
    input_type=_DRINKREQUEST,
    output_type=_DRINKRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_BARTENDER)

DESCRIPTOR.services_by_name['Bartender'] = _BARTENDER

# @@protoc_insertion_point(module_scope)
