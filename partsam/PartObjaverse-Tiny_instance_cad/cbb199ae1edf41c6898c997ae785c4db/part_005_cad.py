"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_005.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_005.stl', 'source_sha256': '8195cb64ca2a29bb52aa9d69b6f4e8238ace24a8fd3100056dd5ecd57f6ca38d', 'input_faces': 290, 'input_vertices': 234, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4291425049304962, -0.36126846075057983, -0.16250666975975037], [0.37501537799835205, 0.09020814299583435, 0.1937449872493744]]}
GEOMETRY_BASE85 = 'c$}r0d5{&=6~=p5qDjCIL_iJUF%kz1AYqB@JV8+ymH}r*K*4620fev&!y<@0#RWkYWfMg57(jMpk>Ie+1BQK_1(3}=Ko<W<DwWDVnuXlk{kv_y^Ey?jWU5YmUw`*Ir*EHL@2km3uUM&u<^I*Pc9k?dHnyf^>8N7WuqNi@<&PMWGrq~_v9G0A)f`>_8C=jat4Bt^6l<b2HEn3l_#t^|Z9-}7a$BV}3Z><a$;;0hH2Re>c|&uw-eu6J@i|H#KYY;G9JSq`S@RZ+Ld_dC3QY_BkAFW=QwUX`bfrjPr2hIf9rc`!cRJG1uV1gVOK-=Ip)b96G0<;x;g8*%=;+q`?-u#}MwkBhzcO8aIRBi+_{cpwihO!#^Xg+7!=qe1T<q%6UEdvcu+r&bziu0SS>{eB|IySV&i2f^PMui8jobZt<lKUz4pPVHHhNN>?|U8f@7MFA$3=ZPPtPyr8Jke=NKhY)p45ky*A55yjV}F>-B%qwvd{I$?oT}!q}y-qPVmR+o9U0yWj~E>?Qr)S7xm-YT|Fl1%l;c(_TSsD=)dO|{rBq6X@4Zh@9F=@JdjXdoG-7wIA7jzRs8-ykUwVhjvEgK>SDi<^ffVOT+Y+z)QK(5a_%d69;I&1qtWGgG`c*GMwjQ&t0T^%(PjU=`G`Jy`xSlm>d5;7UG~kZFZ!0GdwuKg9+$ko(B=ISFJHdY@r&n}(UYEIH8-Ac^hK9Soq2w7?@*9#U%YqJug7AA&U_-mA4L!2x9@a2r7>LXY`MR_)NSF9&7OJM(S<*X9>O1eEA_N<oLjOJ<}Y<y_`~bkmH6i`bu)i!TK4In{z%;xe%T+R%l?FFH#y_@CtWM^*O$62{PDdb&-&|oesohmk{fgN2Hg|-FLhh``_Db&uW$4yy4RnS^s`Ri>h!wcT$ko}g&q<9=(w3D{O8x`5p;8Y?UvR#N3Yl0>2v%_=3&2XquatCJ^r+F9%I5EK{xXc4{zY=!yY{E?~l}N;g4OrcgjD1qes!b`F9!a=;6`b%M#`<bX)jCot`_FFn@Fl-JAczOWgUqJ>a~*|5A@gf5FJa`J+eC&HUrx)Dp*E^Bt$pktb4*1nIGYQ^ykY8AF2o=*DlgYT)RWU8UULAE|ry7kWJUz*&EPj2=Tb{fSn8($&jXC(K9cW<Exb9PS+GH@fjh{=UquQ@QR%fB&U!`fv0|pX29){6?4l@O=wU`p=iqL+Byl53O|HkJ4|Ud;Y(yb@#h!Z^H40ii!gJCUw&XqszWY-8=7%PX}ICQcv=W>q_e0b$Fvrsk7f+Hxv3Sb<<~~hpO5MeKxv<Zu%B0N_F*d`3cvp)NSF9ztQ20|GG7L4BcF}u^w5jze3Y8|M5!Q9Iw%%WmN<HMmK)D?qGMn^?N1wrJm&9_UF<-Kf33iHO1ZUykUv;g)aT!n-@xh{6_b#w@phO-5!*mP+#iOAD(c$G{|ps@4mjWC$PTMrC-*Ux_7+)yd2ygp-X>Ke}wK`|0n+%cz&gx<QL~x>fZg>#wrWCKBX@G^7@pz_Z+_3tSspMlDhX@hc53gqbJ>8cb{@}`FxOiMEK?N!RYe&5WiID?pM4Qq#hA|`CgE^^vm~x(dB!=)5Uwi=<>Y~9@@Cv(ZzdN>bCI9_p;IDdpWj!zpIPy7O6+1UwpS1U4FM%*?)3$`Q0UTTlnR7m(k^SS9D0@^Uiq@-;GkYg<pO*8eM)j#&fgWI^w(6=<>VQ=<>VQt0TU9L+M)`U4FMqJtF+_yWQwX-|Yo|bB|Z7JEU$)zgTw|U9LMKMIA0Uez9(nx-I;2-Q@Y@x@pb^N0;k9soTOY*L_Bp>%Qo$Vn<I}w+h`B{-kxQ(7km*-=-HG6zguO+rlr`-A0$|?nv1BDzHC7w}n5cKj;bl$w>IMx?aDoJ8C~*Svr1f)v$60`F^U_qW&`&{8ROa7XRH()vcTUzdu!1Rddi&(Z5+&Q}HuPPuj)%;Xh@&3Rn&Pkcx*@GyogH^{?=cF#ZT*4>6`a4Z+6n7Al&nNCO{-*9RX1ABR7wqM1Io;IH5zcwO)@_^(wo(LD!$34emIT3~H>Z9KKWI`H49XsRL=tOx%E_$XKp{&N-8Rs0CN58hJ6Z&f@9)__+~QIX3?V+#B!6|GcM0xQGEsTi+fJNN~Bhl-sl^1yt!85;-Y!FQ6I4~~b&Rg|l^3w{ItR>dt9*TM7f>+m>O4!=w8x8N=KWffOd+y?K$?=XG^yavAlzYJc5-zN8tZ+@DWs`y&P4e&PnCgWw`AK_*2Qt)f|4RUY#=BIgk6|GhD0H22URMAOA2e1vi1H3)h8s3B4o?s`q9&fASS@1b{7ZuM_Lt{I58+dE5E&N$>yMWKb^|*ePbq0IEpHY!P4UJ)VJ9t~LBfK-Y&wv^5bUZ`A7vMuxWUA;6hT&!`9qbOzBsUCpgulf0+u$VlJ1Qotcp1!uo3WR`m*JDi%>-Y7Phk5G;Fs`SDhgFh1SiAI*aUDQypY_<;3W7~wvU15;Kx;zsMrP;!p+!La2vdY+(Ph6c#Q3@z;ED}EcYHf0G7bbSPVP>zeR2dcn*F>#eU1ZKQvyjez?CbsyGW4!Ohqi@GSfyxkcc9xPD%3!K3jAT<0CN+-I1^&*5flJGcXWl-$q3E%4qd`dRKXP~%&0{al=(q7T>~ZpM0pec&_5?GN^Y>wCK^9*u+GI&ZM$J`Xf@gPXDTU<deMa=U?D;ipv`RxuFFh7W`f0JGqyR1}j}OpfL!!ECTEJR6<`z6d`-t&^asaR}@S+VH;c7r|HH2dQ-kG&OXLQn3fL;RhMp4eo(!&q#bDsc&-LSFsTs1>eos25=)>duHOBNiCDJS;c$c`|u5ny$ikv*Pc!IHc`vu>{Ib7xEcN~V<W&<;o7qo-(G5&9RGRW2Oq)M0B|5&dy4TDQ%m!?DrTuz2d;*%SFuLLJa9IA9(*o13%-ur_23%#T5vWv2R<7<3;Y278MW5>=CPLX`6>#)&)};Vp96jfp9B8@oDVM`cNMr6zCzSr=&Qd-#qYrn;RU|DRcI^lEX22vS|(?yici2r@D+?L13!Ul&&T*ark2V1RK*f-DSR1Yi@_yu?OBd*IkimAN)-#hPvMIh`v_bB*PbZ8D77@7%l1d$YPinxUq371W^67v559)nm0%S9riy7QMuWNV(eU4aIq-;z*U5XG9L=YLx!`bkE<6Vu27iNE(?L^1kB?C?1$+ZOmGR-=Som=GFmMcf3b|9k>G0Ql^)u2_D%7a>pZ*2vhrfukNbvtdl*~+Aj`}mVs9N6QG$XyTUYn>zNCoFbm!elt*1rMqYV}|'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
